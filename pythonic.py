from twisted.internet import protocol, reactor, endpoints
from twisted.python import log
import sys
import os
import json
import importlib
import inspect
log.startLogging(sys.stdout)

modules = {}

class Runner(protocol.Protocol):
    def dataReceived(self, raw_data):
        requests = [ r for r in raw_data.decode('utf8').split(u'\u2404') if len(r) > 2]
        for data in requests:
            parsed_data = json.loads(str(data))
            command = parsed_data['action']
            if(command == 'RUN'):
                status, body = self.run(parsed_data['module'], parsed_data['function'], parsed_data['args'], parsed_data['kwargs'])

            elif(command == 'IMPORT'):
                status, body = self.importModule(parsed_data['module'])

            elif(command == 'SET_PATH'):
                status, body = self.set_path(parsed_data['path'])

            elif(command == 'INIT_CLASS'):
                status, body = self.init_class(parsed_data['class'], parsed_data['as'], parsed_data['args'], parsed_data['kwargs'])

            else:
                print("Received action of unexpected type. Expected 'RUN' or 'IMPORT', got '" + command + "'.")

            self.transport.write((json.dumps({'pid': parsed_data['pid'], 'status': status, 'body': body}) + u'\u2404').encode('utf8'))




    def run(self, module_name, function_name, function_args, function_kwargs):

        # try:
        call = self.get_module(module_name, function_name)

        result = call(*function_args, **function_kwargs)
        status = 'OK'
        # except KeyboardInterrupt:
        #     raise
        # except Exception as e:
        #     result = e
        #     status = 'ERROR'

        return (status, result)

    def get_module(self, module_name, function_name):
        if len(module_name) > 0:
            module_tree = module_name.split('.')
            module = modules[module_tree.pop(0)]
            while len(module_tree) > 0:
                module = module[module_tree.pop(0)]

        else:
            module_tree = []
            module = modules
        try:
            # the function is attached directly to the nested modules dictionary
            return module[function_name]
        except TypeError:
            # the function is attached to a module or class instance
            return getattr(module, function_name)


    def importModule(self, module_data):
        name = module_data['name']
        from_list = module_data['from_list']
        import_results = __import__(name, globals(), locals(), from_list)
        result = self.attachImport(import_results, name, from_list)

        status = 'OK'
        # except KeyboardInterrupt:
        #     raise
        # except Exception as e:
        #     result = e
        #     status = 'ERROR'

        return (status, result)

    def attachImport(self, import_results, name, from_list=[]):
        # from MODULE import OBJECT1, OBJECT2
        # from PACKAGE.MODULE import OBJECT1, OBJECT2
        # from PACKAGE import MODULE
        if len(from_list) > 0:
            for obj in from_list:
                obj_attr = getattr(import_results, obj)
                if inspect.ismodule(obj_attr):
                    mod_name = obj
                    return self.attachImport(obj_attr, mod_name)
                else:
                    modules[obj] = obj_attr
            result = from_list
        # from MODULE import *
        elif from_list == ['*']:
            d = self.getCallables(import_results)
            for obj in d:
                modules[obj] = getattr(import_results, obj)
            result = d
        # import MODULE
        else:
            d = self.getCallables(import_results)
            modules[name] = import_results
            result = [{name: d}]
        return result

    def getCallables(self, module):
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

            return (status, result)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = 'error setting path'
            status = 'ERROR'

    def init_class(self, classpath, as_name, args, kwargs):
        if '.' in classpath:
            classpath_list = classpath.split('.')
            class_name = classpath_list.pop()
            path = '.'.join(classpath_list)
        else:
            path = ''
            class_name = classpath
        modules[as_name] = self.get_module(path, class_name)(*args, **kwargs)
        result = [{as_name: self.getCallables(modules[as_name])}]
        status = 'OK'

        return (status, result)




class RunnerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Runner()

def onStart():
    print('PYTHONIC_UP')

endpoints.serverFromString(reactor, "tcp:1234").listen(RunnerFactory())
reactor.callWhenRunning(onStart)
reactor.run()
