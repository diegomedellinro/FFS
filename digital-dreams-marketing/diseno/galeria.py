"""Genera digital-dreams-marketing/galeria.html: la vista visual de la semana
(videos, slides y copy listo para copiar) a partir de contenido/*.md.
Uso: python3 digital-dreams-marketing/diseno/galeria.py"""
import base64
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAYS = [
    ("2026-10-13", "Martes 13", "post", "2026-10-13-post-errores-marca", "2026-10-13-carrusel-errores-marca", "2026-10-13-martes-carrusel.md"),
    ("2026-10-14", "Miércoles 14", "reel", "2026-10-14-reel-pov-cliente-ideal", None, "2026-10-14-miercoles-reel.md"),
    ("2026-10-15", "Jueves 15", "post", "2026-10-15-post-bio-que-vende", "2026-10-15-carrusel-bio-que-vende", "2026-10-15-jueves-carrusel.md"),
    ("2026-10-16", "Viernes 16", "reel", "2026-10-16-reel-deja-de-hacer", None, "2026-10-16-viernes-reel.md"),
    ("2026-10-17", "Sábado 17", "post", "2026-10-17-post-checklist", "2026-10-17-carrusel-checklist", "2026-10-17-sabado-carrusel.md"),
    ("2026-10-18", "Domingo 18", "reel", "2026-10-18-reel-ganchos", None, "2026-10-18-domingo-reel.md"),
    ("2026-10-19", "Lunes 19", "post", "2026-10-19-post-mito-logo", "2026-10-19-carrusel-mito-logo", "2026-10-19-lunes-carrusel.md"),
]

logo = "data:image/svg+xml;base64," + base64.b64encode((ROOT / "diseno/logo-icono.svg").read_bytes()).decode()
files = {}  # ruta publicada -> ruta local (para el Artifact)


def asset(rel):
    files[rel] = str(ROOT / rel)
    return rel


cards = []
for date, label, fmt, vid, carousel, md in DAYS:
    text = (ROOT / "contenido" / md).read_text()
    title = re.search(r"^# .*?—\s*(?:REEL|CARRUSEL):\s*(.+)$", text, re.M).group(1)
    hora = re.search(r"\*\*Hora sugerida:\*\*\s*(.+)", text).group(1).strip()
    why = re.search(r"\*\*Por qué funciona:\*\*\s*(.+)", text).group(1).strip()
    copy = re.search(r"## Copy.*?\n```\n(.*?)```", text, re.S).group(1).strip()
    video = asset(f"videos/{vid}.mp4")
    poster = asset(f"videos/{vid}-portada.png")
    slides = ""
    if carousel:
        imgs = sorted((ROOT / "imagenes" / carousel).glob("slide-*.png"))
        slides = '<div class="slides" aria-label="Slides del carrusel">' + "".join(
            f'<img src="{asset(f"imagenes/{carousel}/{p.name}")}" alt="Slide {i + 1}" loading="lazy">' for i, p in enumerate(imgs)
        ) + "</div>"
    kind = "Reel 9:16" if fmt == "reel" else "Post 4:5 · video + carrusel"
    cards.append(f"""
  <article class="day {fmt}" id="d{date[-2:]}">
    <div class="media"><video src="{video}" poster="{poster}" controls muted loop playsinline preload="metadata"></video></div>
    <div class="info">
      <p class="meta"><span class="date">{label} oct</span><span class="pill">{kind}</span><span class="time">{html.escape(hora)}</span></p>
      <h2>{html.escape(title)}</h2>
      <p class="why">{html.escape(why)}</p>
      {slides}
      <div class="copybox">
        <div class="copyhead"><span>Copy para Instagram y Facebook</span><button type="button" class="copy">Copiar copy</button></div>
        <pre>{html.escape(copy)}</pre>
      </div>
    </div>
  </article>""")

page = f"""<title>DigitalDreams Semana 1</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Inter+Tight:wght@400;500;600;700&display=swap');
/* Layout: una tira por día, video a la izquierda y copy a la derecha; colores de la marca (negro + verde lima), tema único oscuro. */
:root {{
  --bg: #050705; --surface: #0D130C; --line: #1F2A1C; --fg: #EEF5EA; --muted: #95A58F; --lime: #8FF20E; --green: #3FA80F; --ink: #041004;
  --display: 'Crimson Pro', Georgia, serif; --body: 'Inter Tight', system-ui, sans-serif;
  color-scheme: dark;
}}
body {{ background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 16px; line-height: 1.5; }}
.wrap {{ max-width: 1120px; margin: 0 auto; padding: 40px 20px 80px; }}
header {{ display: flex; flex-wrap: wrap; align-items: center; gap: 16px 24px; justify-content: space-between; padding-bottom: 28px; border-bottom: 1px solid var(--line); }}
.brand {{ display: flex; align-items: center; gap: 14px; }}
.brand img {{ width: 52px; height: 52px; }}
.brand b {{ font-family: var(--display); font-weight: 400; font-size: 34px; color: #fff; }}
header p {{ color: var(--muted); margin: 0; }}
h1 {{ font-family: var(--display); font-weight: 600; font-size: clamp(36px, 6vw, 60px); line-height: 1.02; margin: 36px 0 8px; text-wrap: balance; }}
h1 em {{ font-style: normal; color: var(--lime); }}
.lede {{ color: var(--muted); max-width: 62ch; margin: 0 0 20px; }}
nav {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 40px; }}
nav a {{ color: var(--fg); text-decoration: none; border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px; font-size: 14px; }}
nav a:hover, nav a:focus-visible {{ border-color: var(--lime); color: var(--lime); outline: none; }}
.day {{ display: grid; grid-template-columns: minmax(0, 340px) minmax(0, 1fr); gap: 32px; padding: 36px 0; border-top: 1px solid var(--line); scroll-margin-top: 16px; }}
.media video {{ width: 100%; display: block; border-radius: 14px; background: #000; border: 1px solid var(--line); }}
.reel .media video {{ aspect-ratio: 9 / 16; }}
.post .media video {{ aspect-ratio: 4 / 5; }}
.info {{ min-width: 0; display: flex; flex-direction: column; gap: 14px; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; margin: 0; font-size: 14px; color: var(--muted); font-variant-numeric: tabular-nums; }}
.date {{ color: var(--lime); font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }}
.pill {{ border: 1px solid var(--green); color: var(--fg); border-radius: 999px; padding: 2px 10px; }}
h2 {{ font-family: var(--display); font-weight: 600; font-size: clamp(26px, 3.4vw, 36px); line-height: 1.1; margin: 0; text-wrap: balance; }}
.why {{ margin: 0; color: var(--muted); max-width: 65ch; }}
.slides {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px; }}
.slides img {{ width: 112px; flex: none; border-radius: 8px; border: 1px solid var(--line); }}
.copybox {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
.copyhead {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 12px 10px 16px; border-bottom: 1px solid var(--line); font-size: 13px; color: var(--muted); }}
button.copy {{ font: 600 14px var(--body); color: var(--ink); background: var(--lime); border: 0; border-radius: 8px; padding: 8px 14px; cursor: pointer; }}
button.copy:focus-visible {{ outline: 2px solid #fff; outline-offset: 2px; }}
pre {{ margin: 0; padding: 16px; white-space: pre-wrap; word-wrap: break-word; font: 15px/1.55 var(--body); color: var(--fg); }}
footer {{ border-top: 1px solid var(--line); padding-top: 24px; color: var(--muted); font-size: 14px; }}
@media (max-width: 720px) {{ .day {{ grid-template-columns: minmax(0, 1fr); }} .media {{ max-width: 360px; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto !important; }} }}
</style>
<div class="wrap">
  <header>
    <div class="brand"><img src="{logo}" alt=""><b>DigitalDreams</b></div>
    <p>Contenido de Instagram y Facebook · semana del 13 al 19 de octubre</p>
  </header>
  <h1>Siete días de contenido, <em>listos para subir</em></h1>
  <p class="lede">Cada día trae su video en motion graphic, las slides del carrusel cuando es post y el copy para pegar. Los videos no llevan música: agrega en Instagram un audio en tendencia antes de publicar.</p>
  <nav>{"".join(f'<a href="#d{d[0][-2:]}">{d[1]}</a>' for d in DAYS)}</nav>
  {"".join(cards)}
  <footer>Agencia DigitalDreams · Marketing digital y branding</footer>
</div>
<script>
document.querySelectorAll('button.copy').forEach((b) => b.addEventListener('click', () => {{
  const pre = b.closest('.copybox').querySelector('pre');
  const done = () => {{ b.textContent = 'Copiado'; setTimeout(() => (b.textContent = 'Copiar copy'), 1600); }};
  const select = () => {{ const r = document.createRange(); r.selectNodeContents(pre); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Seleccionado: copia con Ctrl+C'; }};
  try {{ navigator.clipboard.writeText(pre.textContent).then(done, select); }} catch (e) {{ select(); }}
}}));
</script>
"""
(ROOT / "galeria.html").write_text(page)
(ROOT / "diseno" / "galeria-files.json").write_text(json.dumps(files, indent=1))
print(f"galeria.html · {len(files)} archivos")
