import sys
import os
import json
import importlib
import inspect
import asyncio
from asyncio.streams import FlowControlMixin


# modules = {}
#
# class Runner():
#     def dataReceived(self, raw_data):
#         requests = [ r for r in raw_data.decode('utf8').split(u'\u2404') if len(r) > 2]
#         for data in requests:
#             parsed_data = json.loads(str(data))
#             command = parsed_data['action']
#             if(command == 'RUN'):
#                 status, body = self.run(parsed_data['module'], parsed_data['function'], parsed_data['args'], parsed_data['kwargs'])
#
#             elif(command == 'PING'):
#                 status, body = ('OK', 'PONG')
#
#             elif(command == 'IMPORT'):
#                 status, body = self.importModule(parsed_data['module'])
#
#             elif(command == 'SET_PATH'):
#                 status, body = self.set_path(parsed_data['path'])
#
#             elif(command == 'INIT_CLASS'):
#                 status, body = self.init_class(parsed_data['class'], parsed_data['as'], parsed_data['args'], parsed_data['kwargs'])
#
#             else:
#                 status = 'ERROR'
#                 body = "Received action of unexpected type. Expected 'PING, ''RUN', 'IMPORT', 'SET_PATH', or 'INIT_CLASS'; got '" + command + "'."
#
#             self.transport.write((json.dumps({'pid': parsed_data['pid'], 'status': status, 'body': body}) + u'\u2404').encode('utf8'))
#
#
#
#
#     def run(self, mod_path, function_name, function_args, function_kwargs):
#
#         try:
#             call = self.get_module(mod_path, function_name)
#
#             result = call(*function_args, **function_kwargs)
#             status = 'OK'
#         except KeyboardInterrupt:
#             raise
#         except Exception as e:
#             result = repr(e)
#             status = 'ERROR'
#
#         return (status, result)
#
#     def get_module(self, mod_path, function_name):
#         if len(mod_path) > 0:
#             module_tree = mod_path.split('.')
#             module = modules[module_tree.pop(0)]
#             while len(module_tree) > 0:
#                 module = module[module_tree.pop(0)]
#
#         else:
#             module_tree = []
#             module = modules
#         try:
#             # the function is attached directly to the nested modules dictionary
#             return module[function_name]
#         except (TypeError, AttributeError):
#             # the function is attached to a module or class instance
#             return getattr(module, function_name)
#
#
#     def importModule(self, module_data):
#         try:
#             name = module_data['name']
#             from_list = [str(m) for m in module_data['from_list']]
#             import_results = __import__(name, globals(), locals(), from_list)
#             result = self.attachImport(import_results, name, from_list)
#
#             status = 'OK'
#
#         except KeyboardInterrupt:
#             raise
#         except Exception as e:
#             result = repr(e)
#             status = 'ERROR'
#
#         return (status, result)
#
#     def attachImport(self, import_results, name, from_list=[]):
#         # from MODULE import *
#         if from_list == ['*']:
#             d = self.getCallables(import_results)
#             for obj in d:
#                 modules[obj] = getattr(import_results, obj)
#             result = d
#         # from MODULE import OBJECT1, OBJECT2
#         # from PACKAGE.MODULE import OBJECT1, OBJECT2
#         # from PACKAGE import MODULE
#         elif len(from_list) > 0:
#             for obj in from_list:
#                 obj_attr = getattr(import_results, obj)
#                 if inspect.ismodule(obj_attr):
#                     mod_name = obj
#                     return self.attachImport(obj_attr, mod_name)
#                 else:
#                     modules[obj] = obj_attr
#             result = from_list
#         # import MODULE
#         else:
#             d = self.getCallables(import_results)
#             modules[name] = import_results
#             result = [{name: d}]
#         return result
#
#     def getCallables(self, module):
#         result = []
#         for m in [x for x in dir(module) if not x.startswith('__')]:
#             f = getattr(module, m)
#             if callable(f):
#                 result.append(m)
#         return result
#
#     def set_path(self, path_list):
#         try:
#             for path in path_list:
#                 sys.path.append(os.path.join(os.getcwd(), path))
#             status = 'OK'
#             result = ''
#
#         except KeyboardInterrupt:
#             raise
#         except Exception as e:
#             result = 'error setting path'
#             status = 'ERROR'
#
#         return (status, result)
#
#     def init_class(self, classpath, as_name, args, kwargs):
#         try:
#             if '.' in classpath:
#                 classpath_list = classpath.split('.')
#                 class_name = classpath_list.pop()
#                 path = '.'.join(classpath_list)
#             else:
#                 path = ''
#                 class_name = classpath
#             modules[as_name] = self.get_module(path, class_name)(*args, **kwargs)
#             result = [{as_name: self.getCallables(modules[as_name])}]
#             status = 'OK'
#         except KeyboardInterrupt:
#             raise
#         except Exception as e:
#             result = repr(e)
#             status = 'ERROR'
#
#         return (status, result)

# reader, writer = None, None


# async def start_stdio(loop=None):
#     print('hey!')
#     if loop is None:
#         loop = asyncio.get_event_loop()
#     reader = asyncio.StreamReader()
#     reader_protocol = asyncio.StreamReaderProtocol(reader)
#
#     reader_protocol.data_recieved = handle_message
#
#     writer_transport, writer_protocol = await loop.connect_write_pipe(FlowControlMixin, sys.stdout)
#     writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, loop)
#
#     await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)
#
#     return (reader, writer)

def handle_message():
    print('hey')
    # for line in sys.stdin:
    #     print(line)

async def async_input(message):
    if isinstance(message, str):
        message = message.encode('utf8')

    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = await start_stdio()

    writer.write(message)
    await writer.drain()

    line = await reader.readline()
    return line.decode('utf8').replace('\r', '').replace('\n', '')

@asyncio.coroutine
def main():
    name = yield from async_input("What's your name? ")

    print("Hello, {}!".format(name))


loop = asyncio.get_event_loop()
# start = start_stdio(loop)
loop.add_reader(sys.stdin, handle_message)
# asyncio.ensure_future(start)

loop.run_forever()
