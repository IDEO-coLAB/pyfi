import sys
import traceback
import os
import json
import importlib
import inspect
import asyncio
import signal
import functools
import builtins
import concurrent.futures
import atexit
from contextlib import contextmanager



class PyFiProtocol(asyncio.Protocol):
    def __init__(self, writer_transport, loop):
        super().__init__()
        self.writer_transport = writer_transport
        self.loop = loop

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        atexit.register(functools.partial(self.executor.shutdown, wait=False))

        self.modules = {}

        builtins.print = self.print_to_host

    def data_received(self, data):
        requests = [ r for r in data.decode('utf8').split(u'\u2404') if len(r) > 2]
        for data in requests:
            parsed_data = json.loads(str(data))
            command = parsed_data['action']

            if(command == 'RUN'):
                def handle_result(pid, future):
                    status, body = future.result()
                    self.send_to_host(pid=pid, status=status, body=body)
                future = self.executor.submit(self.run, parsed_data['module'], parsed_data['function'], parsed_data['args'], parsed_data['kwargs'], parsed_data['pid'])
                future.add_done_callback(functools.partial(handle_result, parsed_data['pid']))

            else:
                if(command == 'PING'):
                    status, body = ('OK', 'PONG')

                elif(command == 'IMPORT'):
                    status, body = self.import_module(parsed_data['module'])

                elif(command == 'SET_PATH'):
                    status, body = self.set_path(parsed_data['path'])

                elif(command == 'INIT_CLASS'):
                    status, body = self.init_class(parsed_data['class'], parsed_data['as'], parsed_data['args'], parsed_data['kwargs'])

                else:
                    status = 'ERROR'
                    body = "Received action of unexpected type. Expected 'PING, ''RUN', 'IMPORT', 'SET_PATH', or 'INIT_CLASS'; got '" + command + "'."

                self.send_to_host(pid=parsed_data['pid'], status=status, body=body)


    def send_to_host(self, **kwargs):
        self.writer_transport.write((json.dumps(kwargs) + u'\u2404').encode('utf-8'))

    def print_to_host(self, string, **kwargs):
        self.send_to_host(status='PRINT', body=string)

    def run(self, mod_path, function_name, function_args, function_kwargs, pid):
        def pyfi_message(message):
            self.send_to_host(status='MESSAGE', body=message, pid=pid)

        try:
            builtins.pyfi_message = pyfi_message
            call = self.get_module(mod_path, function_name)
            result = call(*function_args, **function_kwargs)
            builtins.pyfi_message = None
            status = 'OK'
        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = ''.join(traceback.format_exception(*sys.exc_info()))
            status = 'ERROR'

        return (status, result)

    def get_module(self, mod_path, function_name):
        if len(mod_path) > 0:
            module_tree = mod_path.split('.')
            module = self.modules[module_tree.pop(0)]
            while len(module_tree) > 0:
                module = module[module_tree.pop(0)]

        else:
            module_tree = []
            module = self.modules
        try:
            # the function is attached directly to the nested modules dictionary
            return module[function_name]
        except (TypeError, AttributeError):
            # the function is attached to a module or class instance
            return getattr(module, function_name)


    def import_module(self, module_data):
        try:
            name = module_data['name']
            from_list = [str(m) for m in module_data['from_list']]
            import_results = __import__(name, globals(), locals(), from_list)
            result = self.attach_import(import_results, name, from_list)

            status = 'OK'

        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = ''.join(traceback.format_exception(*sys.exc_info()))
            status = 'ERROR'

        return (status, result)

    def attach_import(self, import_results, name, from_list=[]):
        # from MODULE import *
        if from_list == ['*']:
            d = self.get_callables(import_results)
            for obj in d:
                self.modules[obj] = getattr(import_results, obj)
            result = d
        # from MODULE import OBJECT1, OBJECT2
        # from PACKAGE.MODULE import OBJECT1, OBJECT2
        # from PACKAGE import MODULE
        elif len(from_list) > 0:
            for obj in from_list:
                obj_attr = getattr(import_results, obj)
                if inspect.ismodule(obj_attr):
                    mod_name = obj
                    return self.attach_import(obj_attr, mod_name)
                else:
                    self.modules[obj] = obj_attr
            result = from_list
        # import MODULE
        else:
            d = self.get_callables(import_results)
            self.modules[name] = import_results
            result = [{name: d}]
        return result

    def get_callables(self, module):
        result = []
        for m in [x for x in dir(module) if not x.startswith('__')]:
            f = getattr(module, m)
            if callable(f):
                result.append(m)
        return result

    def set_path(self, path_list):
        try:
            for path in path_list:
                sys.path.append(os.path.join(os.getcwd(), path))
            status = 'OK'
            result = ''

        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = 'error setting path'
            status = 'ERROR'

        return (status, result)

    def init_class(self, classpath, as_name, args, kwargs):
        try:
            if '.' in classpath:
                classpath_list = classpath.split('.')
                class_name = classpath_list.pop()
                path = '.'.join(classpath_list)
            else:
                path = ''
                class_name = classpath
            self.modules[as_name] = self.get_module(path, class_name)(*args, **kwargs)
            result = [{as_name: self.get_callables(self.modules[as_name])}]
            status = 'OK'
        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = ''.join(traceback.format_exception(*sys.exc_info()))
            status = 'ERROR'

        return (status, result)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:

        writer = loop.connect_write_pipe(asyncio.BaseProtocol, sys.stdout)
        writer_transport, writer_protocol = loop.run_until_complete(writer)

        reader = loop.connect_read_pipe(functools.partial(PyFiProtocol, writer_transport, loop), sys.stdin)

        loop.add_signal_handler(signal.SIGINT, functools.partial(loop.stop))
        loop.add_signal_handler(signal.SIGTERM, functools.partial(loop.stop))

        loop.run_until_complete(reader)
        loop.run_forever()

    finally:
        loop.close()
