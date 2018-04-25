const net = require('net');
const randomstring = require('randomstring');
const spawn = require('child_process').spawn;
const debug = require('debug')('pythonic');
const path = require('path');


class PyFi {
  constructor(settings) {
    this.startPython = this.startPython.bind(this);
    this.callPython = this.callPython.bind(this);
    this.handlePythonData = this.handlePythonData.bind(this);
    this.importModules = this.importModules.bind(this);
    this.getCallables = this.getCallables.bind(this);
    this.onReady = this.onReady.bind(this);

    this.pythonUp = false;
    this.pythonProcesses = {};
    this.run = {};
    this.moduleTree = [];
    this.port = settings.port;

    this.startPython().then(() => {
      this.setPythonPath(settings.path || '.').then(() => {
        this.importModules(settings.imports).then(() => {
          if (this.readyCallback) {
            this.readyCallback();
          }
        }).catch((error) => { throw error; });
      }).catch((error) => { throw error; });
    }).catch((error) => { throw error; });

    process.on('exit', this.end);
  }


  startPython() {
    return new Promise((resolve, reject) => {
      debug('Starting Python');
      this.pythonProcess = spawn('python', [`${__dirname}/pyfi.py`, this.port], { cwd: '.' });

      this.pythonProcess.stderr.on('data', (error) => {
        if (this.pythonErrorCallback) {
          this.pythonErrorCallback(error);
        } else {
          throw new Error(`PYTHON: ${error.toString()}`);
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

      setTimeout(() => {
        this.callPython({
          action: 'PING',
        }).then(() => {
          this.pythonUp = true;
          resolve();
        });
      }, 200);
    });
  }

  end() {
    this.killPython();
  }


  killPython() {
    this.pythonProcess.kill('SIGINT');
  }

  handlePythonData(data) {
    const res = JSON.parse(data);
    const openProcess = this.pythonProcesses[res.pid];
    if (openProcess) {
      res.status === 'OK' ? openProcess.resolve(res.body) : openProcess.reject(res.body);
      delete this.pythonProcesses[res.pid];
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

  callPython(request) {
    const pid = randomstring.generate(5);
    const fullRequest = `${JSON.stringify(Object.assign(request, { pid }))}\u2404`;
    debug(`Sending: ${fullRequest}`);
    this.pythonProcess.stdin.write(fullRequest);
    // this.pythonProcess.stdin.end();
    return new Promise((resolve, reject) => {
      this.pythonProcesses[pid] = { resolve, reject };
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
