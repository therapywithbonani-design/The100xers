// usage: node render.js w h outdir [frames comma list | all] [shadow]
const { chromium } = require('playwright'); const http = require('http'); const fs = require('fs'); const path = require('path');
const [w, h, outdir, which = 'all', shadow = '2048'] = process.argv.slice(2);
const root = __dirname; const types = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); });
srv.listen(0, async () => {
  const port = srv.address().port; fs.mkdirSync(outdir, { recursive: true });
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 400, height: 400 } });
  p.on('console', m => console.log('[page]', m.text())); p.on('pageerror', e => console.log('[err]', e.message));
  await p.goto(`http://localhost:${port}/index.html?w=${w}&h=${h}&shadow=${shadow}`);
  await p.waitForFunction(() => window.READY === true, null, { timeout: 120000 });
  const meta = await p.evaluate(() => window.META); fs.writeFileSync(path.join(outdir, 'meta.json'), JSON.stringify(meta, null, 1));
  const frames = which === 'all' ? [...Array(meta.NFRAMES).keys()] : which.split(',').map(Number);
  const t0 = Date.now();
  for (const i of frames) {
    const d = await p.evaluate(i => window.renderFrame(i), i);
    fs.writeFileSync(path.join(outdir, `f${String(i).padStart(5, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
    if (i % 60 === 0) console.log('frame', i, '/', meta.NFRAMES, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  await b.close(); srv.close();
});
