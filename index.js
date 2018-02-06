const Tydy = require('./tydy');

const t = new Tydy(['analysis']);

t.onReady(()=>{
  console.log('Tydy up!');
  console.time('tydy')
  t.run.analysis.dummyAnalysis.howLongIsThisString(['yoyoyo!']).then((data)=>{
    console.log(data);
    console.timeEnd('tydy')
  })

  console.time('js')
    console.log('there are ' + 'yoyoyo!'.length + ' characters.' )
  console.timeEnd('js')


})
