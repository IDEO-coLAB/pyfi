# PyFi [![CircleCI](https://circleci.com/gh/IDEO-coLAB/pythonic/tree/master.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/IDEO-coLAB/pythonic/tree/master) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/IDEO-coLAB/pythonic/blob/master/LICENSE)

Use Python from Node ✨

PyFi is designed for prototyping apps with data-driven Python backends. **It is not recommended for scalable or production-ready apps.** For that, you might want to look at a micro-service architecture.

This package can be used along with [pythonic-client](https://github.com/ideo-colab/pyfi-client) to quickly make Python functionality available on the frontend.

### Why?

Python is the language of choice for data science and machine learning (as well as other applications), and a node stack is an excellent choice for prototyping highly-interactive apps. PyFi makes it straightforward to take advantage of both of these strengths simultaneously.

## Installation

**IMPORTANT!** PyFi will install its' own Python dependancies (using pip) after `npm install pyfi`, so be sure that you're working within the python environment used by the Python you'll be importing.

If you already have the Python environment, be sure it's activated and just:
```
npm install pyfi
```

If you're creating a new Python environment when you install this, we'd recommend using [virtualenv](https://virtualenv.pypa.io/en/stable/), which might look something like:
```
virtualenv -p python3 venv
source venv/bin/activate
npm install pyfi
```

## Basic Usage

PyFi mimics how you'd use Python normally.

Say we have this Python module:
`fancycomputation.py`
```py
def my_very_fancy_function(first, second, commentary='nice job!'):
  # ... something fancy you need python for ...
  return str(first + second) + ' commentary'
```

In another Python module, after setting a `PYTHONPATH` to that module, we could call it:
```py
from fancycomputation import my_very_fancy_function

result = my_very_fancy_function(1,2, commentary='hooray!')

print(result)
# 3 hooray!
```

Using PyFi, we can do essentially the same thing in node:
```js
const PyFi = require('pyfi');

const py = PyFi({
  path: './python-stuff', // equivalent to setting PYTHONPATH
  imports: [{
    from: 'fancycomputation',
    import: 'my_very_fancy_function',
  }],
});

// callback for when python has started
py._.onReady(() => {
  py.my_very_fancy_function([1, 2], {commentary: 'way to go!'})
  .then((result) => {
    console.log(result)
    // 3 way to go!
  })
});
```

## Reference

### PyFi({options})
Returns a `PyFi` instance, starts a python kernel and attaches callables in node as described in options.

### Options

**`path`** Array|String

The path or paths to append to the `PYTHONPATH`

**`imports`** Array as `{import, [from]}`

Describes which Python modules to import. Supports these patterns from Python:
```py
from MODULE import OBJECT1, OBJECT2
# {from: 'MODULE' import: ['OBJECT1', 'OBJECT2']}
from PACKAGE import MODULE
# {from: 'PACKAGE', import: 'MODULE'}
import MODULE
# {import: 'MODULE'}
from MODULE import *
# {from: 'MODULE', import: '*'}
```


### Importing and Calling Python Functions

All imports are attached to the `PyFi` instance as they would be to the global namespace in Python. Only callables are made available to Node (not constants).

All calls to Python functions return a promise that resolves to the result.

For example:
```js
const py = PyFi({
  imports:[
    {from: 'my_mod', import: ['my_func', 'my_other_func']}
  ]
 });
```
will make `my_func` and `my_other_func` available:
```js
py.my_func().then(result => {
  console.log(result)
});
py.my_other_func().then(result => {
  console.log(result)
});
```


Similarly if `my_other_mod` contains `do_this()` and `do_that()`, we can run:
```js
const py = PyFi({
  imports:[
    {import: 'my_other_mod'}
  ]
});
```
and now we'll be able to do this:
```js
py.my_other_mod.do_this().then(result => {
  console.log(result)
});
py.my_other_mod.do_that().then(result => {
  console.log(result)
});
```

### Handing arguments to Python
Since JavaScript doesn't have a notion of keyword arguments, instead you can make calls to Python that contain arguments using an array of positional arguments and an object of keyword arguments:

```js
py.my_function([args], {kwargs})
```
You may omit either `[args]` or `{kwargs}` if the function you're calling doesn't require them, but to keep the notation explicit you must always wrap positional arguments in an array.


### Instantiating Python classes
Say you've imported a Python class:
```js
const py = PyFi({
  imports:[
    {from: 'my_mod', import: 'MyClass'}
  ]
});
```
`PyFi` allows you to create and use an instance of that class:
```js
py._.initClass({
    class: 'MyClass',
    as: 'mc',
    args: [/*init args*/],
    kwargs: {/*init kwargs*/}
});
// the initClass method returns a promise
.then(()=>{
  // once the class is init'ed we can call it:
  py.mc.instace_method(['good stuff']).then(result => {
    console.log(result)
  })
});
```
The instance will continue to be available as `py.mc` with all of it's callable methods attached.

### Usage with Pyfi-Client
[PyFi-Client](https://github.com/IDEO-coLAB/pyfi-client) allows for frontend clients to attach to a node instance of PyFi using [socket.io](https://socket.io/). The `_.attachClientSocketIO` method is used to make this functionality available using an existing socket.io instance. You can see a [full example](https://github.com/IDEO-coLAB/pyfi-client/tree/master/example) in the PyFi-Client repo.


### Methods

**`_.onReady(callback)`**

Attach a callback function to call when the instance of PyFi is ready.

**`_.initClass({options})`**

Instantiate a python class and attach it to the instance of PyFi. Returns a Promise. See [Instantiating Python Classes](#instantiating-python-classes) above.

**`_.importModules([modules])`**

Import modules after the initial init. Follows the same pattern as the [init options](#options) (see [Importing and Calling Python Functions](#importing-and-calling-python-functions) for examples).

**`_.attachClientSocketIO(socketIOInstance)`**

Make this instance of PyFi available to [PyFi-Client](https://github.com/IDEO-coLAB/pyfi-client) by attaching an instance of [socket.io](https://socket.io/). See [Usage with PyFi-Client](#usage-with-pyfi-client).

#### What's with the \_?
Since the `py.` namespaces is reserved for the python modules imported by the user, instance methods on the `PyFi` object are proxied to `py._.`.

## Contributing
We welcome issues and pull requests.

If you spot a bug, please provide as much context as possible – including your OS, which versions of Node and Python you're running on, how you're managing your Python environment, and anything else that could be relevant.

## License
MIT License (c) 2018 - Present IDEO CoLab
