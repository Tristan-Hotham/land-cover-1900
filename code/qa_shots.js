// QA: open index.html over a local static server, desktop 1280 px and phone 390 px, log console errors, take screenshots.
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '..');
(async () => {
  const http = require('http'), fs = require('fs');
  const srv = http.createServer((q, s) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; const f = path.join(root, p);
    fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } const ext = path.extname(f); s.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.png': 'image/png', '.json': 'application/json', '.js': 'text/javascript' }[ext] || 'application/octet-stream' }); s.end(d); }); }).listen(0); await new Promise(r => srv.on('listening', r)); const PORT = srv.address().port;
  const b = await chromium.launch();
  for (const [name, w, h] of [['desk', 1280, 900], ['phone', 390, 844]]) {
    const pg = await b.newPage({ viewport: { width: w, height: h } });
    const LD = '/home/claude/newdata/work/land-cover-1900/npm/node_modules/leaflet/dist/';
    await pg.route('**/cdnjs.cloudflare.com/**', r => { const u = r.request().url(); const f = u.endsWith('.css') ? 'leaflet.css' : 'leaflet.js'; r.fulfill({ path: LD + f, contentType: u.endsWith('.css') ? 'text/css' : 'text/javascript' }); });
    await pg.route(/fonts\.(googleapis|gstatic)\.com|arcgisonline/, r => r.abort());
    const errs = [];
    pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    pg.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
    await pg.goto(`http://127.0.0.1:${PORT}/index.html`, { waitUntil: 'load', timeout: 60000 });
    await pg.waitForTimeout(4000);
    await pg.screenshot({ path: `${root}/qa/${name}_top.png` });
    await pg.locator('#atlas').scrollIntoViewIfNeeded(); await pg.waitForTimeout(2500);
    await pg.screenshot({ path: `${root}/qa/${name}_map.png` });
    const mb = await pg.locator('#map').boundingBox();
    await pg.mouse.click(mb.x + mb.width * .32, mb.y + mb.height * .62); await pg.waitForTimeout(1500);
    await pg.screenshot({ path: `${root}/qa/${name}_popup.png` });
    for (const [lay, view] of [['Forest zone', 'Change'], ['Anthromes', 'Swipe 1900 | 2023'], ['Land cover 2019', 'Swipe 1900 | 2023'], ['Cropland', '2023']]) {
      await pg.locator('#viewTabs .btn', { hasText: view }).first().click(); await pg.locator('#layerTabs .btn', { hasText: lay }).click(); await pg.waitForTimeout(2500);
      await pg.locator('#atlas').scrollIntoViewIfNeeded();
      await pg.screenshot({ path: `${root}/qa/${name}_${lay.replace(/\W+/g, '_')}.png` });
    }
    await pg.screenshot({ path: `${root}/qa/${name}_full.png`, fullPage: true });
    const ow = await pg.evaluate(() => document.documentElement.scrollWidth);
    console.log(name, 'scrollWidth', ow, 'errors', JSON.stringify(errs.filter(e => !/arcgisonline|fonts\.g|cdnjs|ERR_|Failed to load resource/.test(e)).slice(0, 8)), 'all', errs.length);
    await pg.close();
  }
  await b.close(); srv.close();
})();
