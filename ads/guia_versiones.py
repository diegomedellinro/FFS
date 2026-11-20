"""Carrusel animado 'Guía de versiones: ¿Jugador o Aficionado?' (6 slides MP4 1080x1350 + portada JPG).
Motion graphics con esquemas propios (sin fotos de terceros), estilo Football Frenzy.
Uso: python3 guia_versiones.py
"""
import math
import os
import subprocess
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text, ease, back, background
from hf_ads import badge
from buenfin_logo import jersey, shadow
from buenfin_2da50 import bg, red, white, pill, RED, GREY, WHITE

OUT = g.HERE + "out/guia_versiones/"
W, H = 1080, 1350
FPS, DUR = 30, 5.5
BG = background(W, H, glows=((0.5, 0.62, 0.8, (150, 10, 18), 0.7), (0.5, 0.05, 0.5, (150, 10, 18), 0.3))).copy()
BEIGE = (190, 60, 66)            # holgura band (brand red, translucent)

# ---------------------------------------------------------------- schematic shirts
FAN = [(-0.42, -0.45), (-0.15, -0.5), (-0.07, -0.46), (0.07, -0.46), (0.15, -0.5), (0.42, -0.45), (0.62, -0.22),
       (0.47, -0.10), (0.36, -0.20), (0.36, 0.50), (-0.36, 0.50), (-0.36, -0.20), (-0.47, -0.10), (-0.62, -0.22)]
PLAYER = [(-0.42, -0.45), (-0.15, -0.5), (-0.07, -0.46), (0.07, -0.46), (0.15, -0.5), (0.42, -0.45), (0.62, -0.22),
          (0.47, -0.10), (0.33, -0.20), (0.30, 0.10), (0.31, 0.50), (0.15, 0.55), (0.0, 0.56), (-0.15, 0.55),
          (-0.31, 0.50), (-0.30, 0.10), (-0.33, -0.20), (-0.47, -0.10), (-0.62, -0.22)]
BODY = 0.28                       # body reference line (half-width)


def shirt(c, cx, cy, s, pts, k, bands=0.0, col=WHITE):
    """Draw the outline progressively (k 0..1) and the 'holgura' bands (bands 0..1)."""
    P = [(cx + x * s, cy + y * s) for x, y in pts] + [(cx + pts[0][0] * s, cy + pts[0][1] * s)]
    d = ImageDraw.Draw(c, "RGBA")
    if bands > 0:
        side = max(abs(x) for x, y in pts if -0.2 < y < 0.5)
        for sg in (-1, 1):
            x0, x1 = cx + sg * BODY * s, cx + sg * side * s
            d.rectangle([min(x0, x1), cy - 0.18 * s, max(x0, x1), cy + 0.5 * s], fill=BEIGE + (int(150 * bands),))
            for yy in range(int(cy - 0.18 * s), int(cy + 0.52 * s), 18):           # dashed body line
                d.line([(x0, yy), (x0, yy + 9)], fill=(200, 200, 205, int(255 * bands)), width=3)
    seg = [math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)]
    left = sum(seg) * k
    for i, L in enumerate(seg):
        if left <= 0:
            break
        f = min(1, left / L)
        a, b = P[i], P[i + 1]
        d.line([a, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)], fill=col + (255,), width=7, joint="curve")
        left -= L


# ---------------------------------------------------------------- shared bits
def head(c, n, t):
    put(c, text("GUÍA DE VERSIONES", "MontB.ttf", 26, RED, 0.25), 250, 80, alpha=ease(t, 0, 0.3))
    put(c, text(f"0{n} / 06", "MontB.ttf", 24, GREY, 0.1), W - 110, 80, alpha=ease(t, 0, 0.3))


def foot(c, s, t, t0=0.6):
    d = ImageDraw.Draw(c)
    k = ease(t, t0, 0.6)
    d.line([(60, H - 105), (60 + (W - 120) * k, H - 105)], fill=(70, 70, 76), width=2)
    put(c, text(s, "MontB.ttf", 24, GREY, 0.08), W / 2, H - 60, alpha=ease(t, t0 + 0.2, 0.4))


def slide_in(c, lay, x, y, t, t0, dx=0, dy=80, dur=0.45):
    k = ease(t, t0, dur)
    if k > 0.01:
        put(c, lay, x + dx * (1 - k), y + dy * (1 - k), alpha=k)


def pop(c, lay, x, y, t, t0, dur=0.4):
    k = back(t, t0, dur)
    if k > 0.01:
        put(c, lay, x, y, alpha=min(1, ease(t, t0, 0.15)), scale=max(0.05, k))


def title(c, lines, t, y0=200, px=120, t0=0.15, colors=None):
    for i, s in enumerate(lines):
        lay = red(s, px, 0.01) if colors and colors[i] else white(s, px, 0.01)
        slide_in(c, lay, W / 2, y0 + i * px * 1.05, t, t0 + i * 0.12, dy=60)


def bullets(c, items, x, y, t, t0, step=0.35, gap=78):
    for i, (b, s) in enumerate(items):
        k = ease(t, t0 + i * step, 0.4)
        if k <= 0.01:
            continue
        row = Image.new("RGBA", (520, 86), (0, 0, 0, 0))
        dd = ImageDraw.Draw(row)
        dd.rectangle([0, 24, 14, 38], fill=RED)
        tb = text(b, "Anton.ttf", 40, WHITE, 0.02)
        row.alpha_composite(tb, (32, 4))
        ts = text(s, "MontB.ttf", 20, GREY, 0.05)
        row.alpha_composite(ts, (34, 62))
        c.alpha_composite(Image.eval(row, lambda v: v) if k >= 1 else _fade(row, k), (int(x + 40 * (1 - k)), int(y + i * gap)))


def _fade(im, k):
    o = im.copy()
    o.putalpha(o.getchannel("A").point(lambda v: int(v * k)))
    return o


# ---------------------------------------------------------------- slides
JER = jersey("rm_home26_v2.png", 520, 0)


def s1(t):
    c = BG.copy()
    head(c, 1, t)
    title(c, ["¿JUGADOR O", "AFICIONADO?"], t, 210, 130, colors=[0, 1])
    slide_in(c, text("LA DIFERENCIA ESTÁ EN CÓMO TE QUEDA", "MontB.ttf", 30, WHITE, 0.04), W / 2, 450, t, 0.5, dy=30)
    k = back(t, 0.7, 0.6)
    if k > 0.01:
        put(c, JER, W / 2, 800, alpha=min(1, ease(t, 0.7, 0.2)), scale=0.85 * k)
    pop(c, pill("AFICIONADO", 40), 230, 1110, t, 1.4)
    pop(c, pill("JUGADOR", 40), W - 230, 1110, t, 1.6)
    put(c, text("MISMO PRECIO · TÚ ELIGES EL CORTE", "MontB.ttf", 26, GREY, 0.1), W / 2, 1190, alpha=ease(t, 2.0, 0.4))
    foot(c, "DESLIZA PARA VER LA GUÍA", t, 2.2)
    return c


def s_version(t, n, name, sub, pts, items):
    c = BG.copy()
    head(c, n, t)
    title(c, [name], t, 200, 150, colors=[1])
    slide_in(c, text(sub, "MontB.ttf", 30, WHITE, 0.03), W / 2, 330, t, 0.35, dy=30)
    shirt(c, 275, 740, 420, pts, ease(t, 0.5, 1.3), ease(t, 1.7, 0.5))
    bullets(c, items, 575, 545, t, 1.2, gap=92)
    put(c, text("ESQUEMA ILUSTRATIVO", "MontB.ttf", 20, GREY, 0.2), 275, 1020, alpha=ease(t, 1.8, 0.4))
    foot(c, "EL AJUSTE Y LOS ACABADOS VARÍAN SEGÚN EL MODELO", t, 2.4)
    return c


def s2(t):
    return s_version(t, 2, "AFICIONADO", "CORTE RECTO, CON HOLGURA", FAN,
                     [("ESCUDO BORDADO", "SE VEN EL HILO Y LA COSTURA"), ("TELA MÁS GRUESA", "AGUANTA EL USO DIARIO"),
                      ("BAJO RECTO", "SE VE BIEN POR FUERA DEL PANTALÓN"), ("IDEAL PARA DIARIO", "CÓMODA Y FÁCIL DE COMBINAR")])


def s3(t):
    return s_version(t, 3, "JUGADOR", "CORTE ENTALLADO, CERCANO AL CUERPO", PLAYER,
                     [("ESCUDO APLICADO", "TERMOSELLADO, SUPERFICIE LISA"), ("TELA LIGERA", "CON MICROPERFORACIONES"),
                      ("BAJO CURVO", "MÁS LARGO ATRÁS"), ("COMO EN LA CANCHA", "LA MISMA QUE USAN LOS JUGADORES")])


def s4(t):
    c = BG.copy()
    head(c, 4, t)
    title(c, ["¿MÁS SUELTA O", "MÁS ENTALLADA?"], t, 190, 110, colors=[0, 1])
    d = ImageDraw.Draw(c)
    k = ease(t, 0.6, 0.5)
    d.line([(W / 2, 470), (W / 2, 470 + 560 * k)], fill=(70, 70, 76), width=2)
    for x, pts, name, s, t0 in ((280, FAN, "AFICIONADO", "SILUETA RECTA Y CON HOLGURA", 0.7),
                                (W - 280, PLAYER, "JUGADOR", "SILUETA CERCANA AL CUERPO", 1.0)):
        shirt(c, x, 730, 400, pts, ease(t, t0, 1.2), ease(t, t0 + 1.2, 0.5))
        slide_in(c, white(name, 60, 0.02), x, 1000, t, t0 + 1.0, dy=40)
        slide_in(c, text(s, "MontB.ttf", 20, GREY, 0.06), x, 1060, t, t0 + 1.2, dy=30)
    # legend
    if t > 2.6:
        a = ease(t, 2.6, 0.4)
        lg = Image.new("RGBA", (W, 50), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lg)
        dd.rectangle([250, 14, 290, 36], fill=BEIGE + (150,))
        lg.alpha_composite(text("HOLGURA", "MontB.ttf", 22, GREY, 0.1), (305, 12))
        for yy in (8, 24):
            dd.line([(560, yy), (560, yy + 9)], fill=(200, 200, 205), width=3)
        lg.alpha_composite(text("LÍNEA DEL CUERPO", "MontB.ttf", 22, GREY, 0.1), (585, 12))
        c.alpha_composite(_fade(lg, a), (0, 1120))
    foot(c, "LA VERSIÓN Y LA TALLA SE ELIGEN POR SEPARADO", t, 2.8)
    return c


ROWS = [("CORTE", "RECTO", "ENTALLADO"), ("ESCUDO", "BORDADO", "APLICADO"), ("FRANJAS", "COSIDAS", "TEJIDAS"),
        ("TELA", "MALLA FINA", "CON RELIEVE"), ("BAJO", "RECTO", "CURVO"), ("IDEAL PARA", "DIARIO", "JUGAR")]


def s5(t):
    c = BG.copy()
    head(c, 5, t)
    title(c, ["LOS DETALLES"], t, 190, 130, colors=[1])
    put(c, text("AFICIONADO", "Anton.ttf", 44, WHITE, 0.05), 560, 340, alpha=ease(t, 0.4, 0.3))
    put(c, text("JUGADOR", "Anton.ttf", 44, RED, 0.05), 850, 340, alpha=ease(t, 0.5, 0.3))
    d = ImageDraw.Draw(c, "RGBA")
    for i, (lab, a, b) in enumerate(ROWS):
        t0 = 0.7 + i * 0.3
        k = ease(t, t0, 0.35)
        if k <= 0.01:
            continue
        y = 420 + i * 120
        d.rounded_rectangle([60 + 40 * (1 - k), y, W - 60, y + 100], radius=18, fill=(20, 20, 24, int(235 * k)))
        for s, x, col, f, px in ((lab, 210, GREY, "MontB.ttf", 24), (a, 560, WHITE, "Anton.ttf", 46), (b, 850, WHITE, "Anton.ttf", 46)):
            put(c, text(s, f, px, col, 0.04), x, y + 50, alpha=k)
    foot(c, "VARÍA SEGÚN EL MODELO", t, 2.8)
    return c


def s6(t):
    c = BG.copy()
    head(c, 6, t)
    title(c, ["ELIGE CÓMO", "QUIERES LLEVARLA"], t, 190, 110, colors=[0, 1])
    small = jersey("rm_home26_v2.png", 190, 0)
    for i, (a, b, x0) in enumerate((("MÁS HOLGADA", "AFICIONADO", 0.6), ("MÁS ENTALLADA", "JUGADOR", 1.2))):
        y = 560 + i * 260
        pop(c, small, 200, y, t, x0)
        slide_in(c, text("SI LA QUIERES", "MontB.ttf", 24, GREY, 0.15), 560, y - 70, t, x0 + 0.1, dx=60, dy=0)
        slide_in(c, white(a, 70, 0.01), 560, y, t, x0 + 0.2, dx=60, dy=0)
        slide_in(c, red(b, 70, 0.01), 560, y + 80, t, x0 + 0.35, dx=60, dy=0)
    slide_in(c, white("¿DUDAS CON TU TALLA?", 54, 0.01), W / 2, 1060, t, 2.0, dy=30)
    slide_in(c, text("ESCRÍBENOS POR DM Y TE AYUDAMOS CON LAS MEDIDAS", "MontB.ttf", 22, GREY, 0.05), W / 2, 1115, t, 2.2, dy=20)
    k = back(t, 2.5, 0.5)
    if k > 0.01:
        put(c, badge(110), W / 2 - 260, 1205, scale=k)
        put(c, pill("GUARDA ESTA GUÍA", 34), W / 2 + 90, 1205, scale=k)
    foot(c, "FOOTBALLFRENZY.SHOP", t, 2.8)
    return c


SLIDES = [s1, s2, s3, s4, s5, s6]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i, fn in enumerate(SLIDES, 1):
        out = f"{OUT}{i:02d}.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                               "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        for n in range(int(DUR * FPS)):
            ff.stdin.write(fn(n / FPS).convert("RGB").tobytes())
        ff.stdin.close()
        ff.wait()
        fn(DUR - 0.1).convert("RGB").save(f"{OUT}{i:02d}.jpg", quality=92, subsampling=0)
    print("ok")
