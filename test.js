const Pythonic = require('./index');

const py = new Pythonic([{
  dir: 'test-python',
  name: 'testpython',
  // package: 'MyPackage',
  objects: [
    'how_long_is_this_string'
  ],
  init: [
    {
      class: 'StringMeasurer',
      as: 'sm',
      args: [],
      kwargs: {}
    }
  ]
},{
  name: 'testpackagemodule',
  package: 'testpackage',
  objects: [
    'give_me_five'
  ]
}])


py.onReady(()=>{
  console.log(py.run)

  py.run.sm.measure_this_string(
    ['howlongisthis??'],    //args
    {}                      //kwargs
  ).then(res => console.log(res))

  py.run.testpython.how_long_is_this_string(
    ['howlongisthis??'],
    {}
  ).then(res => console.log(res))

  py.run.testpackagemodule.give_me_five(
    [],
    {}
  ).then(res => console.log(res))


})
