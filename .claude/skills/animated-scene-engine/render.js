// Usage: node render.js <out.mp4|out_prefix> '<json plan>' [stills]
// plan: [{"scene":"dogwalk","style":"popart","dur":1.5,"label":true}, ...]
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');const fs=require('fs');
const scenes=require('./scenes.js');
(async()=>{const out=process.argv[2],plan=JSON.parse(process.argv[3]),stills=process.argv[4]==='stills';
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:720,height:1280}});p.on('pageerror',e=>console.error('PAGEERR',e.message));
 await p.goto('file://'+path.join(__dirname,'engine.html'));await p.evaluate(()=>window.ready);
 const grab=async(sc,st,t,label)=>{const d=await p.evaluate(([sc,st,t,label])=>{renderScene(sc,st,t);if(label){const x=document.getElementById('c').getContext('2d');x.save();x.font='800 26px Poppins';const s=STY[st].name;const w=x.measureText(s).width+36;x.fillStyle='rgba(0,0,0,.6)';x.beginPath();x.roundRect(24,H-80,w,48,24);x.fill();x.fillStyle='#fff';x.fillText(s,42,H-47);x.restore();}return document.getElementById('c').toDataURL('image/jpeg',.92)},[sc,st,t,label]);return Buffer.from(d.split(',')[1],'base64');};
 if(stills){let i=0;for(const s of plan){fs.writeFileSync(`${out}_${i++}_${s.style}.jpg`,await grab(scenes[s.scene],s.style,s.t||0.4,s.label));}await b.close();return;}
 const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-i','-','-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
 for(const s of plan){const n=Math.round(s.dur*30);for(let f=0;f<n;f++){const buf=await grab(scenes[s.scene],s.style,(s.t0||0)+f/30,s.label);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();})();
