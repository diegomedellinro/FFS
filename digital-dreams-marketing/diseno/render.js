// Genera las slides de carrusel (1080x1350) y portadas de reel (1080x1920)
// a partir de posts.json. Uso: node digital-dreams-marketing/diseno/render.js [id-del-post]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BRAND = 'Digital Dreams Marketing';
const OUT = path.join(__dirname, '..', 'imagenes');
const posts = JSON.parse(fs.readFileSync(path.join(__dirname, 'posts.json'), 'utf8'));

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
// Permite <em> en títulos para resaltar una palabra; todo lo demás se escapa.
const rich = (s) => esc(s).replace(/&lt;em&gt;/g, '<em>').replace(/&lt;\/em&gt;/g, '</em>').replace(/\n/g, '<br>');

const CSS = `
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter Display', 'Inter', sans-serif; color: #F5F3FF; background: #0B0820; }
  .frame { position: relative; overflow: hidden; display: flex; flex-direction: column;
    padding: 96px 88px 80px; background:
      radial-gradient(900px 700px at 110% -10%, rgba(168, 85, 247, .55), transparent 60%),
      radial-gradient(800px 700px at -20% 115%, rgba(34, 211, 238, .35), transparent 60%),
      #0B0820; }
  .frame::after { content: ''; position: absolute; inset: 0; pointer-events: none;
    background-image: radial-gradient(rgba(255,255,255,.07) 1.5px, transparent 1.5px); background-size: 36px 36px; }
  .top { display: flex; justify-content: space-between; align-items: center; font-size: 26px; font-weight: 600;
    letter-spacing: .04em; color: #C4B5FD; position: relative; z-index: 1; }
  .logo { display: flex; align-items: center; gap: 14px; }
  .dot { width: 22px; height: 22px; border-radius: 50%; background: linear-gradient(135deg, #A855F7, #EC4899 55%, #22D3EE); }
  .main { flex: 1; display: flex; flex-direction: column; justify-content: center; position: relative; z-index: 1; }
  .kicker { display: inline-block; align-self: flex-start; font-size: 28px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .12em; padding: 12px 24px; border-radius: 999px; background: rgba(168,85,247,.2);
    border: 2px solid rgba(196,181,253,.5); color: #E9D5FF; margin-bottom: 44px; }
  h1 { font-size: 104px; line-height: 1.02; font-weight: 900; letter-spacing: -.035em; }
  h2 { font-size: 76px; line-height: 1.06; font-weight: 800; letter-spacing: -.03em; margin-bottom: 40px; }
  em { font-style: normal; background: linear-gradient(90deg, #F472B6, #A855F7 50%, #22D3EE);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
  .sub { font-size: 40px; line-height: 1.35; color: #DDD6FE; margin-top: 40px; font-weight: 500; }
  .num { font-size: 200px; font-weight: 900; line-height: .9; letter-spacing: -.05em; margin-bottom: 36px;
    background: linear-gradient(135deg, #F472B6, #A855F7 50%, #22D3EE); -webkit-background-clip: text;
    background-clip: text; color: transparent; }
  .body { font-size: 44px; line-height: 1.4; color: #E4E0F7; font-weight: 500; }
  .card { background: rgba(255,255,255,.06); border: 2px solid rgba(255,255,255,.12); border-radius: 32px; padding: 40px 44px; }
  .label { font-size: 26px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; margin-bottom: 16px; }
  .bad .label { color: #FB7185; } .good .label { color: #34D399; }
  .bad { border-color: rgba(251,113,133,.45); } .good { border-color: rgba(52,211,153,.5); margin-top: 28px; }
  .bad .body { text-decoration: line-through; text-decoration-color: rgba(251,113,133,.7); color: #BDB6D8; }
  ul { list-style: none; display: flex; flex-direction: column; gap: 26px; }
  li { font-size: 46px; font-weight: 600; display: flex; gap: 26px; align-items: center; line-height: 1.2; }
  li::before { content: ''; flex: none; width: 50px; height: 50px; border-radius: 14px; border: 4px solid #A855F7;
    background: rgba(168,85,247,.15); }
  .action { margin-top: 56px; align-self: flex-start; font-size: 38px; font-weight: 800; padding: 30px 44px; border-radius: 24px;
    background: linear-gradient(90deg, #EC4899, #A855F7 55%, #6366F1); color: #fff; }
  .bottom { display: flex; justify-content: space-between; align-items: center; font-size: 28px; font-weight: 600;
    color: #A79FD0; position: relative; z-index: 1; }
  .swipe { color: #F5F3FF; font-weight: 800; }
  .bar { position: absolute; left: 0; bottom: 0; height: 12px; z-index: 2; background: linear-gradient(90deg, #EC4899, #A855F7, #22D3EE); }
  .cover h1 { font-size: 112px; }
  .reel h1 { font-size: 120px; }
  .reel .play { width: 150px; height: 150px; border-radius: 50%; margin-top: 70px; display: grid; place-items: center;
    background: rgba(255,255,255,.12); border: 3px solid rgba(255,255,255,.35); }
  .reel .play::after { content: ''; border-left: 48px solid #fff; border-top: 30px solid transparent; border-bottom: 30px solid transparent; margin-left: 12px; }
`;

function slideInner(s, i, total) {
  switch (s.kind) {
    case 'cover':
      return `<span class="kicker">${esc(s.kicker)}</span><h1>${rich(s.title)}</h1>${s.body ? `<p class="sub">${rich(s.body)}</p>` : ''}`;
    case 'tip':
      return `<div class="num">${esc(s.num)}</div><h2>${rich(s.title)}</h2><p class="body">${rich(s.body)}</p>`;
    case 'list':
      return `<h2>${rich(s.title)}</h2><ul>${s.items.map((it) => `<li>${esc(it)}</li>`).join('')}</ul>`;
    case 'myth':
      return `<div class="card bad"><div class="label">Mito</div><p class="body">${esc(s.myth)}</p></div>
              <div class="card good"><div class="label">Realidad</div><p class="body">${esc(s.truth)}</p></div>`;
    case 'compare':
      return `<h2>${rich(s.title)}</h2>
              <div class="card bad"><div class="label">Antes</div><p class="body">${rich(s.before)}</p></div>
              <div class="card good"><div class="label">Después</div><p class="body">${rich(s.after)}</p></div>`;
    case 'cta':
      return `<h1>${rich(s.title)}</h1><p class="sub">${rich(s.body)}</p>${s.action ? `<div class="action">${esc(s.action)}</div>` : ''}`;
    default:
      throw new Error(`Tipo de slide desconocido: ${s.kind}`);
  }
}

function page(inner, { w, h, cls, index, total }) {
  const last = index === total;
  const bottom = total > 1
    ? `<span>${index}/${total}</span><span class="swipe">${last ? 'Guárdalo ✦' : 'Desliza →'}</span>`
    : `<span>Reel</span><span class="swipe">Mira hasta el final</span>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body>
    <div class="frame ${cls}" style="width:${w}px;height:${h}px">
      <div class="top"><span class="logo"><span class="dot"></span>${BRAND}</span><span>Branding · Marketing</span></div>
      <div class="main">${inner}</div>
      <div class="bottom">${bottom}</div>
      <div class="bar" style="width:${(index / total) * 100}%"></div>
    </div></body></html>`;
}

(async () => {
  const only = process.argv[2];
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ deviceScaleFactor: 1 });
  const pg = await ctx.newPage();
  for (const post of posts) {
    if (only && post.id !== only) continue;
    const dir = path.join(OUT, post.id);
    fs.mkdirSync(dir, { recursive: true });
    const jobs = post.type === 'carousel'
      ? post.slides.map((s, i) => ({ html: page(slideInner(s, i, post.slides.length),
          { w: 1080, h: 1350, cls: s.kind === 'cover' ? 'cover' : '', index: i + 1, total: post.slides.length }),
          w: 1080, h: 1350, name: `slide-${String(i + 1).padStart(2, '0')}.png` }))
      : [{ html: page(`<span class="kicker">${esc(post.kicker)}</span><h1>${rich(post.title)}</h1><div class="play"></div>`,
          { w: 1080, h: 1920, cls: 'reel', index: 1, total: 1 }), w: 1080, h: 1920, name: 'portada-reel.png' }];
    for (const job of jobs) {
      await pg.setViewportSize({ width: job.w, height: job.h });
      await pg.setContent(job.html, { waitUntil: 'load' });
      await pg.evaluate(() => document.fonts.ready);
      await pg.screenshot({ path: path.join(dir, job.name) });
    }
    console.log(`✓ ${post.id} (${jobs.length})`);
  }
  await browser.close();
})();
