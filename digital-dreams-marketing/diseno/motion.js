// Renderiza los posts (1080x1350) y reels (1080x1920) de videos.json como
// motion graphics MP4. Uso: node digital-dreams-marketing/diseno/motion.js [id ...]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const FPS = 30;
const OUT = path.join(__dirname, '..', 'videos');
const videos = JSON.parse(fs.readFileSync(path.join(__dirname, 'videos.json'), 'utf8'));
const BRAND_CSS = require('./brand');
const SIZES = { post: [1080, 1350], reel: [1080, 1920] };

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const CSS = `
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter Display', 'Inter', 'Noto Color Emoji', sans-serif; color: #F4F8F2; background: #030503; overflow: hidden; }
.frame { position: relative; overflow: hidden; background: #030503; }
.blob { position: absolute; border-radius: 50%; filter: blur(90px); opacity: .75; animation: drift 9s ease-in-out infinite alternate both; }
.b1 { width: 900px; height: 900px; right: -380px; top: -360px; background: #2E9E0E; }
.b2 { width: 820px; height: 820px; left: -380px; bottom: -380px; background: #0F4D07; animation-duration: 11s; animation-direction: alternate-reverse; }
.b3 { width: 520px; height: 520px; left: 40%; top: 45%; background: #8FF20E; opacity: .35; animation-duration: 13s; }
@keyframes drift { from { transform: translate(0,0) scale(1); } to { transform: translate(-140px, 120px) scale(1.18); } }
.dots { position: absolute; inset: 0; background-image: radial-gradient(rgba(255,255,255,.08) 1.6px, transparent 1.6px); background-size: 38px 38px; }
.top { position: absolute; left: 88px; right: 88px; top: 80px; display: flex; justify-content: space-between; font-size: 28px; font-weight: 600; letter-spacing: .04em; color: #A3D98A; z-index: 5; }
.logo { display: flex; align-items: center; gap: 14px; }
.dot { width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, #4DBA12, #8FF20E 55%, #C6FF6B); }
.bar { position: absolute; left: 0; bottom: 0; height: 14px; width: 100%; transform-origin: left; z-index: 5;
  background: linear-gradient(90deg, #8FF20E, #4DBA12, #C6FF6B); animation: grow linear both; }
.scene { position: absolute; inset: 0; padding: 200px 88px 140px; display: flex; flex-direction: column; justify-content: center; z-index: 2; }
.reel .scene { padding: 260px 88px 260px; }

/* elementos */
.kicker { align-self: flex-start; font-size: 30px; font-weight: 800; text-transform: uppercase; letter-spacing: .12em; padding: 14px 28px;
  border-radius: 999px; background: rgba(77,186,18,.22); border: 2px solid rgba(143,242,14,.55); color: #E6FFD6; margin-bottom: 48px; }
h1 { font-size: var(--h1); line-height: 1.04; font-weight: 900; letter-spacing: -.035em; }
h2 { font-size: var(--h2); line-height: 1.08; font-weight: 800; letter-spacing: -.03em; margin-bottom: 40px; }
.w { display: inline-block; margin-right: .22em; }
em { font-style: normal; background: linear-gradient(90deg, #B8FF4A, #4DBA12 50%, #C6FF6B); -webkit-background-clip: text; background-clip: text; color: transparent; }
.sub { font-size: 44px; line-height: 1.35; color: #D6E8CF; font-weight: 500; margin-top: 44px; }
.body { font-size: 48px; line-height: 1.38; color: #E3EBDF; font-weight: 500; }
.num { font-size: 240px; font-weight: 900; line-height: .9; letter-spacing: -.05em; margin-bottom: 30px; align-self: flex-start;
  background: linear-gradient(135deg, #B8FF4A, #4DBA12 50%, #C6FF6B); -webkit-background-clip: text; background-clip: text; color: transparent; }
.rule { height: 8px; width: 180px; border-radius: 8px; margin: 10px 0 40px; background: linear-gradient(90deg, #8FF20E, #C6FF6B); transform-origin: left; }
.card { position: relative; background: rgba(255,255,255,.07); border: 3px solid rgba(255,255,255,.14); border-radius: 36px; padding: 44px 48px; }
.label { font-size: 28px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; margin-bottom: 18px; }
.bad { border-color: rgba(251,113,133,.55); } .bad .label { color: #FB7185; }
.good { border-color: rgba(52,211,153,.6); margin-top: 34px; background: rgba(52,211,153,.08); } .good .label { color: #34D399; }
.strikewrap { position: relative; display: inline; }
.strike { position: absolute; left: 40px; right: 40px; top: 58%; height: 7px; border-radius: 7px; background: #FB7185; transform-origin: left; }
ul { list-style: none; display: flex; flex-direction: column; gap: 30px; }
li { font-size: var(--li); font-weight: 650; display: flex; gap: 28px; align-items: center; line-height: 1.18; }
.box { position: relative; flex: none; width: 60px; height: 60px; border-radius: 16px; border: 4px solid #4DBA12; background: rgba(77,186,18,.15); }
.tick { position: absolute; inset: -4px; border-radius: 16px; background: linear-gradient(135deg, #4DBA12, #8FF20E); display: grid; place-items: center;
  font-size: 40px; font-weight: 900; color: #fff; }
.action { align-self: flex-start; margin-top: 60px; }
.btn { display: inline-block; font-size: 44px; font-weight: 800; padding: 34px 54px; border-radius: 28px; color: #fff;
  background: linear-gradient(90deg, #8FF20E, #4DBA12 55%, #2E9E0E); box-shadow: 0 20px 60px rgba(143,242,14,.35); }
.chat { display: flex; flex-direction: column; gap: 44px; }
.msg { max-width: 82%; }
.msg.left { align-self: flex-start; } .msg.right { align-self: flex-end; text-align: right; }
.who { font-size: 28px; font-weight: 700; color: #8FA886; margin: 0 12px 12px; }
.bubble { display: inline-block; font-size: 56px; font-weight: 650; line-height: 1.2; padding: 34px 44px; border-radius: 44px; text-align: left; }
.left .bubble { background: rgba(255,255,255,.12); border-bottom-left-radius: 12px; }
.right .bubble { background: linear-gradient(135deg, #4DBA12, #8FF20E); border-bottom-right-radius: 12px; }
.bigemoji { font-size: 300px; line-height: 1; align-self: center; }
.center { text-align: center; align-items: center; }
.stopbadge { position: relative; align-self: flex-start; width: 190px; height: 190px; border-radius: 50%; display: grid; place-items: center;
  font-size: 110px; font-weight: 900; background: rgba(251,113,133,.14); border: 5px solid #FB7185; color: #FECDD3; margin-bottom: 50px; }
.stamp { position: absolute; right: -40px; top: -30px; font-size: 34px; font-weight: 900; letter-spacing: .1em; color: #fff; background: #E11D48;
  padding: 12px 22px; border-radius: 14px; }
.ghost { position: absolute; right: 40px; top: 190px; font-size: 620px; font-weight: 900; line-height: 1; color: transparent;
  -webkit-text-stroke: 4px rgba(143,242,14,.22); z-index: -1; }
.quote { font-size: 104px; font-weight: 850; line-height: 1.08; letter-spacing: -.03em; }
.score { display: flex; flex-direction: column; gap: 26px; }
.row { display: flex; align-items: center; gap: 34px; font-size: 48px; font-weight: 650; }
.pill { flex: none; width: 210px; text-align: center; padding: 18px 0; border-radius: 22px; font-weight: 900; font-size: 46px; }
.r0 .pill { background: #059669; } .r1 .pill { background: #D97706; } .r2 .pill { background: #E11D48; }

/* animaciones */
.pop { animation: pop 650ms cubic-bezier(.34,1.56,.64,1) both; }
.up { animation: up 700ms cubic-bezier(.22,1,.36,1) both; }
.slide { animation: slide 600ms cubic-bezier(.22,1,.36,1) both; }
.grow { animation: grow 500ms cubic-bezier(.65,0,.35,1) both; }
.stampin { animation: stamp 420ms cubic-bezier(.34,1.56,.64,1) both; }
.shake { animation: shake 900ms ease-in-out both; }
.pulse { animation: pulse 1100ms ease-in-out infinite both; }
@keyframes pop { from { opacity: 0; transform: scale(.4); } to { opacity: 1; transform: none; } }
@keyframes up { from { opacity: 0; transform: translateY(70px); filter: blur(8px); } to { opacity: 1; transform: none; filter: none; } }
@keyframes slide { from { opacity: 0; transform: translateX(-90px); } to { opacity: 1; transform: none; } }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes stamp { from { opacity: 0; transform: scale(2.6) rotate(-14deg); } to { opacity: 1; transform: rotate(-8deg); } }
@keyframes shake { 0%,100% { transform: none; } 20% { transform: rotate(-9deg); } 40% { transform: rotate(8deg); } 60% { transform: rotate(-5deg); } 80% { transform: rotate(3deg); } }
@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.06); } }
`;

// Divide un título en palabras animadas, manteniendo el resaltado <em>.
function words(title, t0, step = 85) {
  const out = [];
  const re = /<em>(.*?)<\/em>|(\S+)/g;
  let m;
  while ((m = re.exec(title))) {
    if (m[1] !== undefined) m[1].split(/\s+/).forEach((w) => out.push(`<em>${esc(w)}</em>`));
    else out.push(esc(m[2]));
  }
  return { html: out.map((w, i) => `<span class="w up" style="animation-delay:${t0 + i * step}ms">${w}</span>`).join(''), end: t0 + out.length * step };
}

function scene(s, at) {
  const d = (ms) => `style="animation-delay:${at + ms}ms"`;
  switch (s.type) {
    case 'hook': {
      const w = words(s.title, at + 350);
      return `${s.kicker ? `<span class="kicker pop" ${d(100)}>${esc(s.kicker)}</span>` : ''}<h1>${w.html}</h1>
        ${s.sub ? `<p class="sub up" style="animation-delay:${w.end + 200}ms">${esc(s.sub)}</p>` : ''}`;
    }
    case 'tip':
      return `<div class="num pop" ${d(80)}>${esc(s.num)}</div><div class="rule grow" ${d(350)}></div>
        <h2 class="up" ${d(450)}>${esc(s.title)}</h2><p class="body up" ${d(800)}>${esc(s.body)}</p>`;
    case 'stop':
      return `<div class="stopbadge pop" ${d(80)}>${esc(s.num)}<span class="stamp stampin" ${d(900)}>STOP</span></div>
        <h2 class="up" ${d(400)}>${esc(s.title)}</h2><p class="body up" ${d(1300)}>${esc(s.body)}</p>`;
    case 'list': {
      const step = Math.min(520, (s.dur - 1900) / s.items.length);
      return `<h2 class="up" ${d(100)}>${esc(s.title)}</h2><ul>${s.items.map((it, i) =>
        `<li class="slide" ${d(550 + i * step)}><span class="box"><span class="tick pop" ${d(800 + i * step)}>✓</span></span>${esc(it)}</li>`).join('')}</ul>`;
    }
    case 'myth':
      return `<div class="card bad up" ${d(100)}><div class="label">Mito</div><p class="body"><span class="strikewrap">${esc(s.myth)}</span></p>
          <span class="strike grow" ${d(1000)}></span></div>
        <div class="card good up" ${d(1500)}><div class="label">Realidad</div><p class="body">${esc(s.truth)}</p></div>`;
    case 'compare':
      return `<h2 class="up" ${d(100)}>${esc(s.title)}</h2>
        <div class="card bad up" ${d(350)}><div class="label">Antes</div><p class="body">${esc(s.before)}</p><span class="strike grow" ${d(1200)}></span></div>
        <div class="card good up" ${d(1700)}><div class="label">Después</div><p class="body">${esc(s.after)}</p></div>`;
    case 'chat':
      return `<div class="chat">${s.msgs.map((m, i) =>
        `<div class="msg ${m.side} pop" ${d(250 + i * 1500)}><div class="who">${esc(m.name)}</div><div class="bubble">${esc(m.text)}</div></div>`).join('')}</div>`;
    case 'big':
      return `<div class="center" style="display:flex;flex-direction:column"><div class="pop" ${d(50)}><div class="bigemoji shake" ${d(600)}>${s.emoji}</div></div>
        <h2 class="up" ${d(400)} style="margin-top:40px">${esc(s.text)}</h2></div>`;
    case 'quote': {
      const w = words(s.text, at + 300, 70);
      return `<div class="ghost pop" ${d(0)}>${esc(s.num)}</div><span class="kicker pop" ${d(80)}>Gancho ${esc(s.num)}</span><div class="quote">${w.html}</div>`;
    }
    case 'score':
      return `<h2 class="up" ${d(100)}>${esc(s.title)}</h2><div class="score">${s.rows.map((r, i) =>
        `<div class="row r${i} slide" ${d(600 + i * 650)}><span class="pill">${esc(r[0])}</span>${esc(r[1])}</div>`).join('')}</div>`;
    case 'cta': {
      const w = words(s.title, at + 100);
      return `<h1>${w.html}</h1>${s.body ? `<p class="sub up" style="animation-delay:${w.end + 150}ms">${esc(s.body)}</p>` : ''}
        ${s.action ? `<div class="action pop" style="animation-delay:${w.end + 500}ms"><span class="btn pulse" style="animation-delay:${w.end + 1200}ms">${esc(s.action)}</span></div>` : ''}`;
    }
    default:
      throw new Error(`Escena desconocida: ${s.type}`);
  }
}

function buildHtml(v) {
  const [w, h] = SIZES[v.format];
  let at = 0;
  const keyframes = [];
  const scenes = v.scenes.map((s, i) => {
    const last = i === v.scenes.length - 1;
    const inP = (450 / s.dur) * 100;
    const outP = ((s.dur - 380) / s.dur) * 100;
    keyframes.push(`@keyframes life${i} { 0% { opacity: 0; transform: translateY(50px) scale(.98); }
      ${inP.toFixed(2)}% { opacity: 1; transform: none; }
      ${last ? '100% { opacity: 1; transform: none; }' : `${outP.toFixed(2)}% { opacity: 1; transform: none; } 100% { opacity: 0; transform: translateY(-50px) scale(.98); }`} }`);
    const html = `<section class="scene" style="animation: life${i} ${s.dur}ms linear ${at}ms both">${scene(s, at)}</section>`;
    at += s.dur;
    return html;
  });
  const vars = v.format === 'reel' ? '--h1:122px;--h2:86px;--li:56px' : '--h1:104px;--h2:78px;--li:50px';
  return {
    total: at,
    html: `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}${BRAND_CSS}${keyframes.join('\n')}</style></head><body>
      <div class="frame ${v.format}" style="width:${w}px;height:${h}px;${vars}">
        <div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="dots"></div>
        <div class="top"><span class="logo"><span class="dot"></span><span class="wm">DigitalDreams</span></span><span>Marketing Digital</span></div>
        ${scenes.join('\n')}
        <div class="bar" style="animation-duration:${at}ms"></div>
      </div></body></html>`,
  };
}

async function render(browser, v) {
  const [w, h] = SIZES[v.format];
  const { html, total } = buildHtml(v);
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => document.getAnimations().forEach((a) => a.pause()));
  const seek = (t) => page.evaluate((t) => document.getAnimations().forEach((a) => { a.currentTime = t; }), t);
  if (process.env.PREVIEW) {
    // Vista previa: guarda cuadros sueltos (ms separados por comas) en vez del video.
    for (const t of process.env.PREVIEW.split(',').map(Number)) {
      await seek(t);
      await page.screenshot({ path: path.join(process.env.PREVIEW_DIR || OUT, `${v.id}-${t}.png`) });
    }
    return page.close();
  }
  fs.mkdirSync(OUT, { recursive: true });
  const file = path.join(OUT, `${v.id}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', (c) => (c === 0 ? res() : rej(new Error(`ffmpeg ${c}`)))));
  const frames = Math.ceil((total / 1000) * FPS);
  for (let f = 0; f < frames; f++) {
    await seek((f * 1000) / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await done;
  // Portada: el gancho ya completo, justo antes de salir.
  await seek(v.scenes[0].dur - 500);
  await page.screenshot({ path: path.join(OUT, `${v.id}-portada.png`) });
  await page.close();
  console.log(`✓ ${v.id} (${(total / 1000).toFixed(1)} s)`);
}

(async () => {
  const ids = process.argv.slice(2);
  const browser = await chromium.launch();
  for (const v of videos) if (!ids.length || ids.includes(v.id)) await render(browser, v);
  await browser.close();
})();
