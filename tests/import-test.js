var test = require('tape');
const Pythonic = require('../')

test('import MODULE', (t)=>{
  t.plan(1);
  const py = new Pythonic({
    path: './test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: 'test_module'
    }]
  })
  py.test_module.how_long_is_this_string('12').then(res =>{
    t.equal(res, 2)
  })
})

test('from MODULE import OBJECT', (t)=>{
  t.plan(1);
  const py = new Pythonic({
    path: './test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: ['how_long_is_this_string', 'StringMeasurer'],
      from: 'test_module'
    }]
  })
  py.how_long_is_this_string('12').then(res =>{
    t.equal(res, 2)
  })
  // TODO: should this be moved to a separate test?
  py._init(class: 'StringMeasurer', as: 'sm').then( () =>{
    py.sm.measure_this_string('123').then( res => {
      t.equal(res, 3)
    })
  })
})


test('from PACKAGE.MODULE import OBJECT', (t)=>{
  t.plan(1);
  const py = new Pythonic({
    path: './test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: 'give_me_five',
      from: 'test_package.test_package_module'
    }]
  })
  py.give_me_five().then(res =>{
    t.equal(res, 5)
  })
})


test('from PACKAGE import MODULE', (t)=>{
  t.plan(1);
  const py = new Pythonic({
    path: './test-python', // equivalent to setting PYTHONPATH
    imports: [{
      import: 'test_package_module',
      from: 'test_package'
    }]
  })
  py.test_package_module.give_me_five().then(res =>{
    t.equal(res, 5)
  })
})
