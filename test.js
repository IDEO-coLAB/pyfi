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
}])

py.onReady(()=>{
  console.log(py.run)
  py.run.sm.measure_this_string(['howlongisthis??'],{}).then(res => console.log(res))

})
