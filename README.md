**This is in alpha! Try it out & tell us how it goes! Okay!**

# PyFi [![CircleCI](https://circleci.com/gh/IDEO-coLAB/pyfi/tree/master.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/IDEO-coLAB/pyfi/tree/master) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/IDEO-coLAB/pyfi/blob/master/LICENSE) [![npm](https://img.shields.io/npm/v/pyfi.svg)](https://www.npmjs.com/package/pyfi)


Call Python functions from Node with an asynchronous architecture ✨

PyFi is designed for prototyping Node apps with data-driven Python backends. It runs Python as a subprocess of Node, which will get you up and running quickly for prototyping, but is not recommended for a production environment.

This package can be used along with [pyfi-client](https://github.com/ideo-colab/pyfi-client) to quickly make Python functionality available to a javascript client.

### Why?

Python is the language of choice for data science and machine learning (as well as other applications), and a node stack is great for prototyping highly-interactive apps. PyFi makes it straightforward to take advantage of both of these strengths simultaneously.

## Compatibility

Requires Node 6+ and Python 3.4+


## Installation

PyFi no longer has any Python dependancies, so to install you can just:
```
npm install pyfi
```

## Basic Usage

PyFi mimics how you'd use Python normally.

Say we have this Python module:
`fancycomputation.py`
```py
def my_very_fancy_function(first, second, commentary='nice job!'):
  # ... something fancy you need python for ...
  return str(first + second) + ' ' + commentary
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

// callback for when pythonic is ready
py._.onReady(() => {
  // we wrap args in an array and kwargs in an object
  py.my_very_fancy_function([1, 2], {commentary: 'way to go!'})
  .then((result) => {
    console.log(result)
    // 3 way to go!
  })
});
```

## Reference

### PyFi({options})
Returns a `PyFi` instance, starts a Python kernel and attaches callables in node as described in options.

### Options

**`path`** Array|String

The path or paths to append to the `PYTHONPATH`

**`imports`** Array as `{import, [from]}`

Describes which Python modules to import. Supports these patterns from Python:

| Python                                | Pyfi                                              |
| ------------------------------------- | ------------------------------------------------- |
| `from MODULE import OBJECT1, OBJECT2` | `{from: 'MODULE' import: ['OBJECT1', 'OBJECT2']}` |
| `from PACKAGE import MODULE`          | `{from: 'PACKAGE', import: 'MODULE'}`             |
| `import MODULE`                       | `{import: 'MODULE'}`                              |
| `from MODULE import *`                | `{from: 'MODULE', import: '*'}`                   |

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

### Sending messages through PyFi while a function is running
PyFi includes handling for sending back from Python while a function is running. That allows for, for example, streaming status back to a client while a long-running function is in progress. To accomplish that, a function `pyfi_message` is injected into the run context, which is received by an `onMessage` handler attached to the corresponding promise.

That looks like this:
Python:
```py
def my_function():
  # ... do something ...
  pyfi_message('my message')
  # ... do something else ...
  return 'done!'
```
Node:
```js
// assuming you've imported this function already
py.my_function()
  .onMessage(data => {
    console.log(data)
    // 'my message'
  })
  .then(res => {
    console.log(res);
    // 'done'
  })
```



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
})
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

Attach a callback for when the instance of PyFi is ready.

**`_.onPrint(callback)`**

Attach a callback for when python prints. By default it will be `console.log`ed and denote as `PYTHON:`.

```js
py._.onPrint((message) => {
  console.log(`Here's what python said: ${message}`)
})
```

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
