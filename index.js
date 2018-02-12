const Pythonic = require('./pythonic');

console.time('pythonic-whole')

const py = new Pythonic(['analysis']);

py.onReady(()=>{
  console.log('Pythonic up!');
  console.time('pythonic')
  py.run.analysis.dummyAnalysis.howLongIsThisString(['yoyoyo!']).then((data)=>{
    console.log(data);
    console.timeEnd('pythonic')
    console.timeEnd('pythonic-whole')
  })

  console.time('js')
    console.log('there are ' + 'yoyoyo!'.length + ' characters.' )
  console.timeEnd('js')

})
