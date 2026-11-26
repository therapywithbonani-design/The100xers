const http=require('http'),fs=require('fs'),path=require('path');
const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2','.ttf':'font/ttf'};
http.createServer((q,s)=>{let p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));fs.readFile(p,(e,d)=>{if(e){s.writeHead(404);s.end();return}s.writeHead(200,{'content-type':mime[path.extname(p)]||'application/octet-stream'});s.end(d)})}).listen(8765,()=>console.log('up'));
