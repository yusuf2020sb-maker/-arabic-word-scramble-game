// Renders a reel page frame by frame: node rec.js <page.html> <outDir> <fps> <seconds> [t1,t2,...]
// The page must expose window.render(t). Pass explicit times to render only those frames.
const { chromium } = require('playwright');
(async () => {
  const [html, out, fps, dur, only] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + html);
  await p.waitForLoadState('networkidle');
  await p.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => i.decode().catch(() => {})));
  });
  const times = only ? only.split(',').map(Number) : [...Array(Math.round(fps * dur)).keys()].map((i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    await p.evaluate((t) => new Promise((r) => { render(t); requestAnimationFrame(() => requestAnimationFrame(r)); }), times[i]);
    await p.screenshot({ path: `${out}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
