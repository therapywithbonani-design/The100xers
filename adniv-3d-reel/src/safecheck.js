const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--enable-webgl']});
 const p=await b.newPage({viewport:{width:1080,height:1920}}); p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('http://localhost:8765/engine.html'); await p.waitForFunction('window.ready===true',{timeout:180000});
 let worst={l:1e9,r:-1e9,t:1e9,b:-1e9}, viol=[], n=0;
 for(let T=0.2;T<53.6;T+=0.4){
  await p.evaluate(`window.renderShot('reel','B',${T})`);
  const r=await p.evaluate(()=>{const out=[];const q=(sel,name)=>document.querySelectorAll(sel).forEach(e=>{let o=1,x=e;while(x&&x.id!=='hud'){o*=parseFloat(getComputedStyle(x).opacity);x=x.parentElement}
    if(o<0.35||getComputedStyle(e).display==='none')return;const b=e.getBoundingClientRect();if(b.width<2||b.height<2)return;out.push({n:name,l:b.left,r:b.right,t:b.top,b:b.bottom})});
   q('#h-chip','chip');q('#h-logo','logo');q('#h-head .ch','head');q('#h-head .hsub','sub');q('#h-cap span','cap');q('#h-lbl','label');q('#h-src b','src');q('.pill','pill');q('.lab','lab');
   q('.cta .card','cta-card');q('.cta .sub','cta-sub');q('.cta .or','cta-or');q('.cta .btn','cta-btn');q('.cta .web u','cta-web');q('#c-h .ch','cta-head');return out});
  for(const e of r){n++;
   if(e.n==='head'||e.n==='cta-head'){e.l-=10;e.r+=12;e.b+=14}                                    // extrusion + shadow allowance
   const over=[e.l<64?'L':'',e.r>1016?'R':'',e.t<230?'T':'',e.b>1500?'B':'',(e.r>940&&e.b>1000&&e.t<1500&&e.n!=='cta-web'&&e.n!=='cta-btn'&&e.n!=='cta-sub'&&e.n!=='cta-or'&&e.n!=='cta-card'&&e.n!=='cta-head'&&e.l>0&&e.r>940)?'ICON':''].join('');
   worst.l=Math.min(worst.l,e.l);worst.r=Math.max(worst.r,e.r);worst.t=Math.min(worst.t,e.t);worst.b=Math.max(worst.b,e.b);
   if(over)viol.push(`${T.toFixed(1)}s ${e.n} ${over} l${e.l|0} r${e.r|0} t${e.t|0} b${e.b|0}`);}
 }
 console.log('elements checked',n,'| extremes: left',worst.l|0,'right',worst.r|0,'top',worst.t|0,'bottom',worst.b|0);
 console.log('violations',viol.length); console.log(viol.slice(0,25).join('\n'));
 await b.close();})();
