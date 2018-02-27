from twisted.internet import protocol, reactor, endpoints
from twisted.python import log
import sys
import os
import json
import importlib
log.startLogging(sys.stdout)

sys.path.append(os.path.join(os.getcwd(), '../drugbust/data-science'))

print(sys.path)

# from modelmanager import ModelManager
#
# print(dir(ModelManager))
#
# m = ModelManager()


modules = {}



class Runner(protocol.Protocol):
    def dataReceived(self, data):
        parsed_data = json.loads(data)
        command = parsed_data['action']
        if(command == 'RUN'):
            status, body = self.run(parsed_data['module'], parsed_data['function'], parsed_data['args'], parsed_data['kwargs'])

        elif(command == 'IMPORT'):
            status, body = self.importModule(parsed_data['module'])

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
        if 'dir' in module_data:
            sys.path.append(os.path.join(os.getcwd(), module_data['dir']))
            print(sys.path)
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

        print(dir(module))

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



class RunnerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Runner()

def onStart():
    print('PYTHONIC_UP')

endpoints.serverFromString(reactor, "tcp:1234").listen(RunnerFactory())
reactor.callWhenRunning(onStart)
reactor.run()
