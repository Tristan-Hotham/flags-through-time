// QA: serve the folder, open index.html at 1280 px and 390 px, collect console errors, take screenshots, exercise the controls.
// Run from anywhere: node code/12_qa.js (needs playwright; Leaflet and topojson-client from a local npm folder, QA_NODE).
const { chromium } = require('playwright');
const path = require('path'), http = require('http'), fs = require('fs');
const NM = process.env.QA_NODE || '/tmp/claude-0/qa/node_modules';
const ROOT = path.resolve(__dirname, '..');
const TYPES = { '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.csv': 'text/csv', '.js': 'text/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0].split('#')[0])); fs.readFile(f.endsWith('/') ? f + 'index.html' : f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  const b = await chromium.launch();
  for (const [w, h, tag] of [[1280, 900, 'desktop'], [390, 844, 'phone']]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    const errs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    p.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
    await p.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
    await p.route(/leaflet.min.js/, r => r.fulfill({ path: NM + '/leaflet/dist/leaflet.js' }));
    await p.route(/leaflet.min.css/, r => r.fulfill({ path: NM + '/leaflet/dist/leaflet.css' }));
    await p.route(/topojson-client.min.js/, r => r.fulfill({ path: NM + '/topojson-client/dist/topojson-client.min.js' }));
    await p.goto(`http://localhost:${srv.address().port}/index.html`, { waitUntil: 'load' });
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_top.png` });
    await p.evaluate(() => document.getElementById('atlas').scrollIntoView());
    for (const y of [1000, 1492, 1783, 1914, 2010]) {
      await p.evaluate(y => setYear(YEARS.indexOf(y)), y); await p.waitForTimeout(1400);
      await p.screenshot({ path: `${ROOT}/qa/${tag}_map_${y}.png` });
    }
    await p.evaluate(() => { S.fill = 'colours'; restyle(); placeLabels(); legend(); }); await p.waitForTimeout(500);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_2010_colours.png` });
    await p.evaluate(() => { S.fill = 'auto'; }); 
    await p.evaluate(() => setYear(YEARS.indexOf(1783)).then(() => { map.setView([42, -75], 4.5); }).then(() => 0)); await p.waitForTimeout(1500);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_1783_zoom.png` });
    await p.evaluate(() => { const f = CUR.feats.find(f => SITE.owners[f.properties.o] && SITE.owners[f.properties.o].n === 'United States'); featureClick(f, L.latLng(42.36, -71.06)); }); await p.waitForTimeout(500);
    await p.evaluate(() => document.getElementById('side').scrollIntoView({ block: 'center' })); await p.waitForTimeout(300);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_click.png` });
    await p.evaluate(() => setYear(YEARS.indexOf(1600)).then(() => map.setView([47, 12], 4.5)).then(() => 0)); await p.waitForTimeout(1500);
    await p.evaluate(() => document.getElementById('atlas').scrollIntoView()); await p.waitForTimeout(300);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_1600_europe.png` });
    await p.evaluate(() => searchFor('Venice')); await p.waitForTimeout(200);
    const sug = await p.$eval('#sug', e => e.textContent);
    await p.click('#play'); await p.waitForTimeout(3500); await p.click('#play');
    const yr = await p.$eval('#yrlab', e => e.textContent);
    for (const id of ['coverChart', 'bigChart', 'euroChart', 'cityChart', 'statesChart', 'ageChart']) {
      await p.evaluate(id => document.getElementById(id).scrollIntoView({ block: 'center' }), id); await p.waitForTimeout(250);
      await p.screenshot({ path: `${ROOT}/qa/${tag}_${id}.png` });
    }
    const fsb = await p.$$eval('.mfs-btn', e => e.length);
    const sw = await p.evaluate(() => document.documentElement.scrollWidth);
    console.log(tag, 'fullscreen buttons', fsb, 'scrollWidth', sw, 'year after play', yr, 'search:', sug.slice(0, 90));
    console.log(tag, 'errors', errs.filter(e => !/ERR_|net::|Failed to load resource/.test(e)), 'network errors', errs.filter(e => /ERR_|net::|Failed to load resource/.test(e)).length);
    await p.close();
  }
  await b.close(); srv.close();
})();
