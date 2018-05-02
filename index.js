const randomstring = require('randomstring');
const spawn = require('child_process').spawn;
const debug = require('debug')('pyfi');

class PyFiPromise extends Promise {
  // message, resolve, reject
  constructor(fn) {
    fn.bind(this, this.sendMessageCallback);
    super(fn);
  }
  onMessage(callback) {
    this.sendMessageHandler = callback;
  }
}

class PyFi {
  constructor(settings) {
    this.onPythonError = this.onPythonError.bind(this);
    this.startPython = this.startPython.bind(this);
    this.pythonUp = false;
    this.pythonProcesses = {};
    this.run = {};
    this.moduleTree = [];

    this.startPython().then(() => {
      this.setPythonPath(settings.path || '.').then(() => {
        this.importModules(settings.imports).then(() => {
          if (this.readyCallback) {
            this.readyCallback();
          }
        }).catch((error) => { console.log('Importing modules failed.', error); });
      }).catch((error) => { console.log('Error setting python path.', error); });
    }).catch((error) => { console.log('Failed to start Python.', error); });

    process.on('exit', this.end);
  }


  startPython() {
    return new Promise((resolve, reject) => {
      debug('Starting Python');
      this.pythonProcess = spawn('python', [`${__dirname}/pyfi.py`], { cwd: '.' });

      this.pythonProcess.stderr.on('data', (error) => {
        const errorString = error.toString();
        if (this.pythonErrorCallback) {
          this.pythonErrorCallback(errorString);
        } else if (this.pythonUp) {
          throw new Error(`PYTHON: ${errorString}`);
        }
      });

      this.pythonProcess.stdout.on('data', (data) => {
        debug('Received:', data.toString());
        data.toString().split('\u2404').forEach((res) => {
          if (res.length > 2) {
            this.handlePythonData(res);
          }
        });
      });

      this.callPython({
        action: 'PING',
      }).then(() => {
        this.pythonUp = true;
        resolve();
      });
    });
  }

  end() {
    this.pythonUp = false;
    this.killPython();
  }


  killPython() {
    this.pythonProcess.kill('SIGINT');
  }

  handlePythonData(data) {
    const res = JSON.parse(data);
    const openProcess = this.pythonProcesses[res.pid];

    if (openProcess) {
      switch (res.status) {
        case 'OK':
          openProcess.resolve(res.body);
          break;
        case 'MESSAGE':
          if (openProcess.messageHandler) {
            openProcess.messageHandler(res.body);
          }
        default:
          openProcess.reject(res.body);
          break;
      }
      delete this.pythonProcesses[res.pid];
    } else if (res.status === 'PRINT') {
      if (this.pythonPrintCallback) {
        this.pythonPrintCallback(res.body);
      } else {
        console.log(`PYTHON: ${res.body}`);
      }
    }
  }

  setPythonPath(path) {
    return this.callPython({
      action: 'SET_PATH',
      path: Array.isArray(path) ? path : [path],
    });
  }

  importModules(modules) {
    // console.log(modules)
    return new Promise((resolve, reject) => {
      modules.forEach((module) => {
        this.callPython({
          action: 'IMPORT',
          module: {
            name: module.from ? module.from : module.import,
            // TODO: fix nested ternary cuz who do you think you are?
            from_list: module.from ? Array.isArray(module.import) ? module.import : [module.import] : [],
          },
        })
          .then((results) => {
            this.handleImportResults(results);
            resolve();
          })
          .catch(reject);
      });
    });
  }

  initClass(options) {
    return new Promise((resolve, reject) => {
      this.callPython(Object.assign(
        {
          action: 'INIT_CLASS',
          // set defaults for args and kwargs
          args: [],
          kwargs: {},
        },
        // merge options over defaults
        options,
      ))
        .then((results) => {
          this.handleImportResults(results);
          resolve();
        })
        .catch(reject);
    });
  }

  handleImportResults(results) {
    this.moduleTree = this.moduleTree.concat(results);
    this.run = Object.assign({}, this.run, this.getCallables(results));
  }

  getCallables(moduleTree, treeLoc) {
    return moduleTree.reduce((result, element) => {
      const isFunc = typeof element === 'string';
      const modName = treeLoc || '';
      if (isFunc) {
        result[element] = (args = [], kwargs = {}) => this.callPython({
          action: 'RUN',
          module: modName,
          function: element,
          // TODO: allow for more natural handling of args and kwargs
          args: Array.isArray(args) ? args : [],
          kwargs: Array.isArray(args) ? kwargs : args,
        });
      } else {
        const subModName = Object.keys(element)[0];
        const nextSubModName = modName ? `${modName}.${subModName}` : subModName;
        result[subModName] = this.getCallables(element[subModName], nextSubModName);
      }
      return result;
    }, {});
  }

  onReady(callback) {
    this.readyCallback = callback;
  }

  onPythonError(callback) {
    this.pythonErrorCallback = callback;
  }

  onPrint(callback) {
    this.pythonPrintCallback = callback;
  }

  callPython(request) {
    const pid = randomstring.generate(5);
    const fullRequest = `${JSON.stringify(Object.assign(request, { pid }))}\u2404`;
    debug(`Sending: ${fullRequest}`);
    this.pythonProcess.stdin.write(fullRequest);
    const onMessage = (handler);
    const result = new Promise((resolve, reject) => {
      this.pythonProcesses[pid] = {
        message,
        resolve,
        reject,
      };
    });
  }

  attachClientSocketIO(io) {
    io.on('connection', (socket) => {
      debug('SocketIO connected');
      socket.on('pythonic-run', (req) => {
        debug('Recieved SocketIO request', req);
        debug('REQUEST', req.request);
        this.callPython(req.request).then((res) => {
          socket.emit('pythonic-run-data', { rid: req.rid, data: res });
        });
      });
      socket.on('pythonic-get-modules', () => {
        socket.emit('pythonic-modules', this.moduleTree);
      });
    });
  }
}

const proxyHandler = {
  get: (target, key, receiver) => {
    if (key === '_') {
      return target;
    } else if (target.run && key in target.run) {
      return target.run[key];
    }
    return undefined;
  },
};

module.exports = settings => new Proxy(new PyFi(settings), proxyHandler);
