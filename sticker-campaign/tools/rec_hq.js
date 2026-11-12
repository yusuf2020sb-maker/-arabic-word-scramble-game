// High-quality renderer: draws each frame at 2x (2160x3840) and streams PNGs to ffmpeg,
// which downsamples with lanczos to 1080x1920 (supersampled edges, no frames on disk).
// usage: node rec_hq.js <page.html> <fps> <seconds> <audio.wav> <out.mp4> [loudnorm]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const [html, fps, dur, audio, out, ln] = process.argv.slice(2);
  const af = (ln === 'loudnorm' ? 'loudnorm=I=-16:TP=-1.5,' : '') + 'aresample=48000,pan=stereo|c0=c0|c1=c0';
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'png', '-i', '-', '-i', audio,
    '-filter_complex', `[0:v]scale=1080:1920:flags=lanczos[v];[1:a]${af}[a]`, '-map', '[v]', '-map', '[a]', '-shortest',
    '-c:v', 'libx264', '-preset', 'slower', '-crf', '12', '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 2 });
  await p.goto('file://' + html);
  await p.waitForLoadState('networkidle');
  await p.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map((i) => i.decode().catch(() => {}))); });
  const n = Math.round(fps * dur);
  for (let i = 0; i < n; i++) {
    await p.evaluate((t) => new Promise((r) => { render(t); requestAnimationFrame(() => requestAnimationFrame(r)); }), i / fps);
    const buf = await p.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await b.close();
  await new Promise((r) => ff.on('close', r));
})();
