from twisted.internet import protocol, reactor, endpoints
from twisted.python import log
import sys
import os
import json
import importlib
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

            else:
                print("Received action of unexpected type. Expected 'RUN' or 'IMPORT', got '" + command + "'.")

            self.transport.write((json.dumps({'pid': parsed_data['pid'], 'status': status, 'body': body}) + u'\u2404').encode('utf8'))




    def run(self, module_name, function_name, function_args, function_kwargs):

        # try:
        # TODO: How efficient is this? Seems like it could be a drag.
        module_tree = module_name.split('.')
        module = modules[module_tree.pop(0)]
        while len(module_tree) > 0:
            module = getattr(module, module_tree.pop(0))
        result = getattr(module, function_name)(*function_args, **function_kwargs)
        status = 'OK'
        # except KeyboardInterrupt:
        #     raise
        # except Exception as e:
        #     result = e
        #     status = 'ERROR'

        return (status, result)

    def importModule(self, module_data):
        # try:
        name = module_data['name']
        if 'package' in module_data:
            module = importlib.import_module('.' + name, package=module_data['package'])
        else:
            module = importlib.import_module(name)


        modules[name] = module

        result = []
        callables = self.getCallables(module)

        if 'objects' in module_data:
            callables = list(set(callables) & set(module_data['objects']))

        result.append({'name': name, 'callables': callables})

        if 'init' in module_data:
            for c in module_data['init']:
                modules[c['as']] = getattr( module, c['class'])(*c['args'], **c['kwargs'])
                result.append({'name': c['as'], 'callables': self.getCallables(modules[c['as']])})

        status = 'OK'
        # except KeyboardInterrupt:
        #     raise
        # except Exception as e:
        #     result = e
        #     status = 'ERROR'

        return (status, result)

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




class RunnerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Runner()

def onStart():
    print('PYTHONIC_UP')

endpoints.serverFromString(reactor, "tcp:1234").listen(RunnerFactory())
reactor.callWhenRunning(onStart)
reactor.run()
