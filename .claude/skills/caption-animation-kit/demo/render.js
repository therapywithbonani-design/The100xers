const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{const dir=process.argv[2],out=process.argv[3],only=process.argv[4];
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:720,height:1280}});
 p.on('pageerror',e=>console.error('PAGEERR',e.message));
 await p.goto('file://'+dir+'/index.html');await p.evaluate(()=>window.ready);
 const N=await p.evaluate(()=>window.TOTAL_FRAMES);
 if(only){for(const f of only.split(',')){const d=await p.evaluate(f=>{render(+f);return document.getElementById('c').toDataURL('image/jpeg',.9)},f);
   require('fs').writeFileSync(out+'_'+f+'.jpg',Buffer.from(d.split(',')[1],'base64'));}await b.close();return;}
 const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-i','-','-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-c:a','aac','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
 for(let f=0;f<N;f++){const d=await p.evaluate(f=>{render(f);return document.getElementById('c').toDataURL('image/jpeg',.92)},f);
  if(!ff.stdin.write(Buffer.from(d.split(',')[1],'base64')))await new Promise(r=>ff.stdin.once('drain',r));}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('frames',N);})();
