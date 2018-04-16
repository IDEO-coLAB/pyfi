const test = require('tape');
const PyFi = require('../');

// TODO: we need proper error handling for rejected promises!!

test('import MODULE', (t) => {
  t.plan(1);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: 'test_module',
    }],
  });
  py._.onReady(() => {
    py.test_module.how_long_is_this_string(['12']).then((res) => {
      t.equal(res, 2);
      py._.end();
    }).catch((error) => {
      t.fail(error);
      py._.end();
    });
  });
});

test('from MODULE import OBJECT', (t) => {
  t.plan(1);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: ['how_long_is_this_string', 'StringMeasurer'],
      from: 'test_module',
    }],
  });
  py._.onReady(() => {
    py.how_long_is_this_string(['12']).then((res) => {
      t.equal(res, 2);
      py._.end();
    }).catch((error) => {
      t.fail(error);
      py._.end();
    });
  });
});

test('from MODULE import *', (t) => {
  t.plan(1);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: '*',
      from: 'test_module',
    }],
  });
  py._.onReady(() => {
    py.how_long_is_this_string(['12']).then((res) => {
      t.equal(res, 2);
      py._.end();
    }).catch((error) => {
      t.fail(error);
      py._.end();
    });
  });
});

test('from BUILTIN_MODULE import OBJECT', (t) => {
  t.plan(1);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: 'time',
      from: 'time',
    }],
  });
  py._.onReady(() => {
    py.time().then((res) => {
      t.pass(`time: ${res}`);
      py._.end();
    }).catch((error) => {
      t.fail(error);
      py._.end();
    });
  });
});


test('from MODULE import OBJECT, init class', (t) => {
  t.plan(1);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: ['how_long_is_this_string', 'StringMeasurer'],
      from: 'test_module',
    }],
  });
  py._.onReady(() => {
    py._.initClass({ class: 'StringMeasurer', as: 'sm' }).then(() => {
      py.sm.measure_this_string(['123']).then((res) => {
        t.equal(res, 3);
        py._.end();
      }).catch((error) => {
        t.fail(error);
        py._.end();
      });
    }).catch((error) => {
      t.fail(error);
      py._.end();
    });
  });
});


test('from PACKAGE.MODULE import OBJECT', (t) => {
  t.plan(1);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: 'give_me_five',
      from: 'test_package.test_package_module',
    }],
  });
  py._.onReady(() => {
    py.give_me_five().then((res) => {
      t.equal(res, 5);
      py._.end();
    }).catch((error) => {
      t.fail(error);
      py._.end();
    });
  });
});

test('from PACKAGE import MODULE', (t) => {
  t.plan(1);
  const py = PyFi({
    path: './tests/test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: 'test_package_module',
      from: 'test_package',
    }],
  });
  py._.onReady(() => {
    py.test_package_module.give_me_five().then((res) => {
      t.equal(res, 5);
      py._.end();
    }).catch((error) => {
      t.fail(error);
      py._.end();
    });
  });
});
