// node render.js <look> <shot> <t0> <t1> <fps> <outDir> [prefix]   (t0==t1 -> single still)
const {chromium}=require('playwright'); const fs=require('fs');
const [look,shot,t0,t1,fps,out,prefix='f']=process.argv.slice(2);
(async()=>{
 fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--enable-webgl']});
 const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>console.log('PAGEERROR',e.message)); p.on('console',m=>{const s=m.text(); if(!/GPU stall|GL Driver/.test(s)) console.log('console:',s)});
 await p.goto('http://localhost:8765/engine.html'); await p.waitForFunction('window.ready===true',{timeout:120000});
 const T0=+t0,T1=+t1,F=+fps; const n=T1>T0?Math.round((T1-T0)*F):1; const t_=Date.now();
 for(let i=0;i<n;i++){const t=T0+i/F; await p.evaluate(`window.renderShot(${JSON.stringify(shot)},${JSON.stringify(look)},${t})`);
  const buf=await p.screenshot({type:'png'}); fs.writeFileSync(`${out}/${prefix}_${String(i).padStart(4,'0')}.png`,buf);
  if(n>1&&i%15==0) console.log(`${look} ${shot} frame ${i}/${n} ${((Date.now()-t_)/(i+1)/1000).toFixed(2)}s/f`);}
 await b.close();
})();
