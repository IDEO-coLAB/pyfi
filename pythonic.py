from twisted.internet import protocol, reactor, endpoints
from twisted.python import log
import sys
import os
import json
import importlib
log.startLogging(sys.stdout)

import analysis

modules = {}

def importModule(module_data):
    if 'dir' in module_data:
        sys.path.append(os.path.join(os.getcwd(), module_data['dir']))
    name = module_data['name']
    if 'from' in module_data:
        module = importlib.import_module('.' + name, module_data['from'])
    else:
        module = importlib.import_module(name)
    modules[name] = module
    return module

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

        self.transport.write(json.dumps({'pid': parsed_data['pid'], 'status': status, 'body': body}) + 	u'\u2404'.encode('utf8'))




    def run(self, module_name, function_name, function_args, function_kwargs):

        try:
            # TODO: How efficient is this? Seems like it could be a drag.
            module_tree = module_name.split('.')
            module = modules[module_tree.pop(0)]
            while len(module_tree) > 0:
                module = getattr(module, module_tree.pop(0))
            result = getattr(module, function_name)(*function_args, **function_kwargs)
            status = 'OK'
        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = e
            status = 'ERROR'

        return (status, result)

    def importModule(self, module_data):
        try:
            module = importModule(module_data)
            result = self.getModuleTree(module)
            status = 'OK'
        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = e
            status = 'ERROR'

        return (status, result)

    def getModuleTree(self, module):
        result = []
        print( dir(module))
        for m in [x for x in dir(module) if not x.startswith('__')]:
            f = getattr(module, m)
            if callable(f):
                result.append(m)
                return result
            else:
                result.append({m: self.getModuleTree(getattr(module, x))})
                return result



class RunnerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Runner()

def onStart():
    print('PYTHONIC_UP')

endpoints.serverFromString(reactor, "tcp:1234").listen(RunnerFactory())
reactor.callWhenRunning(onStart)
reactor.run()
