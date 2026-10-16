"""Creativos para Meta Ads (feed 4:5, historias 9:16 y videos) de Football Frenzy.

Cada concepto es una función frame(W, H, t) que dibuja el cuadro en el segundo t.
- La imagen estática es el último estado de la animación (todo visible).
- En los videos, el cuadro 0 ya muestra el gancho (la primera frase), para que el
  primer segundo detenga el scroll y la miniatura nunca salga vacía.
- Historias 9:16: el texto clave queda entre el 13% y el 80% de la altura
  (arriba y abajo los tapa la interfaz de Instagram).

Fuentes de producto: ads/src (recortes de las fotos de la tienda; reseñas reales de clientes).
Uso:
  python3 generar_ads.py                 # todas las imágenes
  python3 generar_ads.py --video         # imágenes + videos
  python3 generar_ads.py --video trio    # solo un concepto
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from functools import lru_cache
import math, os, sys, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
SRC, FONTS, OUT = HERE + "src/", HERE + "fonts/", HERE + "out/"
INTER = "/usr/share/fonts/opentype/inter/"

RED = (226, 20, 32)
WHITE = (255, 255, 255)
GREY = (170, 170, 175)
INK = (8, 8, 10)
GOLD = (236, 196, 92)

FEED, STORY = (1080, 1350), (1080, 1920)
FPS = 30


# ---------------------------------------------------------------- basics

@lru_cache(None)
def font(name, px):
    path = FONTS + name if os.path.exists(FONTS + name) else INTER + name
    return ImageFont.truetype(path, int(px))


def ease(t, t0, dur=0.45):
    """0→1 ease-out-cubic between t0 and t0+dur."""
    if t <= t0:
        return 0.0
    k = min(1.0, (t - t0) / dur)
    return 1 - (1 - k) ** 3


def back(t, t0, dur=0.5):
    """Ease-out with a small overshoot (for stamps / badges)."""
    if t <= t0:
        return 0.0
    k = min(1.0, (t - t0) / dur)
    c = 1.9
    return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2


@lru_cache(None)
def src(name):
    return Image.open(SRC + name).convert("RGBA")


@lru_cache(512)
def fit(name, w, h):
    im = src(name)
    s = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


@lru_cache(512)
def with_shadow(name, w, h):
    """Product cut-out with a soft floor shadow, padded so the blur is not clipped."""
    im = fit(name, w, h)
    p = int(max(im.size) * 0.12)
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p, p + int(im.height * 0.035)))
    a = a.filter(ImageFilter.GaussianBlur(max(6, im.width * 0.03))).point(lambda v: int(v * 0.75))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 255))
    sh.putalpha(a)
    out.alpha_composite(sh)
    out.alpha_composite(im, (p, p))
    out.pad = p
    return out


def put(canvas, layer, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    """Paste an RGBA layer centred on (cx, cy) with opacity/scale/rotation."""
    if alpha <= 0.01:
        return
    if scale != 1.0:
        layer = layer.resize((max(1, round(layer.width * scale)), max(1, round(layer.height * scale))), Image.BICUBIC)
    if rot:
        layer = layer.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def product(canvas, name, cx, cy, w, h, alpha=1.0, scale=1.0, rot=0.0):
    lay = with_shadow(name, int(w), int(h))
    put(canvas, lay, cx, cy, alpha, scale, rot)


# ---------------------------------------------------------------- text layers

@lru_cache(1024)
def text(s, fname, px, fill=WHITE, track=0.0, strike=None):
    """Tight RGBA layer of a single line; track is letter-spacing in em; strike draws a line through it."""
    f = font(fname, px)
    asc, desc = f.getmetrics()
    tw = sum(f.getlength(c) for c in s) + track * px * max(0, len(s) - 1)
    bb = f.getbbox(s)
    top, bot = bb[1], bb[3]
    pad = int(px * 0.15)
    im = Image.new("RGBA", (int(tw) + 2 * pad, bot - top + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad
    for c in s:
        d.text((x, pad - top), c, font=f, fill=fill)
        x += f.getlength(c) + track * px
    if strike:
        y = im.height // 2
        d.line([(pad - px * 0.05, y), (im.width - pad + px * 0.05, y)], fill=strike, width=max(3, int(px * 0.09)))
    return im


@lru_cache(256)
def rich(parts, fname, px, track=0.0):
    """One line made of (text, color) parts."""
    f = font(fname, px)
    full = "".join(s for s, _ in parts)
    bb = f.getbbox(full, anchor="ls")
    pad = int(px * 0.15)
    w = int(sum(f.getlength(ch) + track * px for s, _ in parts for ch in s)) + 2 * pad
    im = Image.new("RGBA", (w, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, base = pad, pad - bb[1]
    for s, c in parts:
        for ch in s:
            d.text((x, base), ch, font=f, fill=c, anchor="ls")
            x += f.getlength(ch) + track * px
    return im


@lru_cache(256)
def pill(s, fname, px, bg=RED, fg=WHITE, padx=0.7, pady=0.38, outline=None, track=0.02):
    t = text(s, fname, px, fg, track)
    w, h = int(t.width + px * padx * 2), int(t.height + px * pady * 2)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=bg, outline=outline, width=max(3, px // 12) if outline else 0)
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return im


@lru_cache(64)
def stars(px, n=5, fill=GOLD):
    gap = px * 0.18
    im = Image.new("RGBA", (int(n * px + (n - 1) * gap) + 2, int(px) + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(n):
        cx, cy, R, r = i * (px + gap) + px / 2, px / 2 + 1, px / 2, px * 0.2
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = R if k % 2 == 0 else r
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=fill)
    return im


@lru_cache(64)
def checks(items, px, color=WHITE, tick=RED):
    """Row of '✓ item' benefits (tick drawn as a red circle with a white check)."""
    f = font("Inter-SemiBold.otf", px)
    gap, cr = px * 1.1, px * 0.62
    widths = [f.getlength(s) for s in items]
    W = int(sum(widths) + len(items) * (2 * cr + px * 0.45) + gap * (len(items) - 1)) + 4
    H = int(max(2 * cr, px * 1.3)) + 4
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 2
    for s, w in zip(items, widths):
        cy = H / 2
        d.ellipse([x, cy - cr, x + 2 * cr, cy + cr], fill=tick)
        lw = max(2, int(px * 0.13))
        d.line([(x + cr * 0.55, cy + cr * 0.02), (x + cr * 0.88, cy + cr * 0.35), (x + cr * 1.45, cy - cr * 0.38)], fill=WHITE, width=lw, joint="curve")
        x += 2 * cr + px * 0.45
        bb = f.getbbox(s)
        d.text((x, cy - (bb[1] + bb[3]) / 2), s, font=f, fill=color)
        x += w + gap
    return im


@lru_cache(16)
def brand(px):
    """Small 'FOOTBALL FRENZY' wordmark with a red dot (text only, no crest)."""
    t = text("FOOTBALL FRENZY", "MontB.ttf", px, WHITE, 0.22)
    r = px * 0.32
    im = Image.new("RGBA", (int(t.width + r * 3), t.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, im.height / 2 - r, 2 * r, im.height / 2 + r], fill=RED)
    im.alpha_composite(t, (int(r * 2.6), 0))
    return im


@lru_cache(16)
def cta(label, w, px):
    """Full-width red call-to-action bar with an arrow."""
    h = int(px * 2.3)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=RED)
    t = text(label, "Anton.ttf", px, WHITE, 0.04)
    aw = px * 0.9
    x0 = (w - t.width - aw * 1.4) / 2
    im.alpha_composite(t, (int(x0), (h - t.height) // 2))
    ax, ay = x0 + t.width + aw * 0.35, h / 2
    lw = max(4, int(px * 0.13))
    d.line([(ax, ay), (ax + aw, ay)], fill=WHITE, width=lw)
    d.line([(ax + aw * 0.55, ay - aw * 0.42), (ax + aw, ay), (ax + aw * 0.55, ay + aw * 0.42)], fill=WHITE, width=lw, joint="curve")
    return im


# ---------------------------------------------------------------- backgrounds

@lru_cache(32)
def background(W, H, glows=((0.5, 0.55, 0.55, RED, 0.55),), base=INK):
    """Black base + soft radial colour glows + vignette + fine grain. glows: (x, y, radius·W, color, strength)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32) + np.array(base, np.float32)
    for gx, gy, gr, col, k in glows:
        d = np.sqrt((xx - gx * W) ** 2 + (yy - gy * H) ** 2) / (gr * W)
        a = np.clip(1 - d, 0, 1) ** 2.2 * k
        img = img * (1 - a[..., None]) + np.array(col, np.float32) * a[..., None]
    v = np.sqrt(((xx / W - 0.5) * 1.1) ** 2 + ((yy / H - 0.5) * 0.9) ** 2)
    img *= np.clip(1.15 - v * 0.9, 0.35, 1)[..., None]
    rng = np.random.default_rng(7)
    img += rng.normal(0, 3.2, (H, W, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


@lru_cache(8)
def stripes(W, H, color=WHITE, alpha=10, step=46):
    """Faint diagonal pitch-like stripes."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in range(-H, W + H, step * 2):
        d.polygon([(x, 0), (x + step, 0), (x + step - H * 0.4, H), (x - H * 0.4, H)], fill=color + (alpha,))
    return im


class Frame:
    """Layout helper: safe vertical band depends on the format."""
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.story = H / W > 1.5
        self.top = H * (0.13 if self.story else 0.055)
        self.bot = H * (0.80 if self.story else 0.95)
        self.cx = W / 2

    def y(self, k):
        """k in [0,1] → y inside the safe band."""
        return self.top + (self.bot - self.top) * k


def footer(c, L, t, t0, label="COMPRA EN FOOTBALLFRENZY.SHOP", items=("Envío gratis", "Tallas S a 4XL", "Pago seguro")):
    """Benefits row + CTA bar at the bottom of the safe band."""
    W = L.W
    a1, a2 = ease(t, t0), ease(t, t0 + 0.25)
    row = checks(items, 30)
    if row.width > W * 0.9:
        row = checks(items, 26)
    bar = cta(label, int(W * 0.84), 40)
    yb = L.bot - bar.height / 2
    put(c, bar, L.cx, yb + (1 - a2) * 40, a2)
    put(c, row, L.cx, yb - bar.height / 2 - row.height * 1.1 + (1 - a1) * 30, a1)


def head(c, L, t=99):
    put(c, brand(26), L.cx, L.top + 18, 1)


# ---------------------------------------------------------------- concepts

def trio(W, H, t):
    """3x2: 'Lleva 3, paga 2' — tres jerseys entran, la tercera sale GRATIS, luego la cuenta."""
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.52, 0.62, RED, 0.5),)).copy()
    c.alpha_composite(stripes(W, H))
    head(c, L)
    # hook — visible from frame 0
    h1 = rich((("LLEVA ", WHITE), ("3", RED)), "Anton.ttf", 150 if L.story else 132)
    h2 = rich((("PAGA ", WHITE), ("2", RED)), "Anton.ttf", 150 if L.story else 132)
    pulse = 1 + 0.025 * math.sin(t * 2.4) if t > 3.2 else 1
    y0 = L.y(0.08) + 30
    put(c, h1, L.cx, y0, 1, pulse)
    put(c, h2, L.cx, y0 + h1.height * 0.92, 1, pulse)
    # three jerseys
    jy = L.y(0.47 if L.story else 0.45)
    jh = H * (0.23 if L.story else 0.24)
    jw = W * 0.40
    items = [("arg_last.png", -0.31, 0.35, -7), ("america110.png", 0.31, 0.95, 7), ("mu0708.png", 0.0, 1.55, 0)]
    for name, dx, t0, rot in items:
        k = ease(t, t0, 0.55)
        fl = math.sin((t - t0) * 1.6 + dx * 4) * 6 if t > t0 + 0.6 else 0
        x = L.cx + dx * W + (1 - k) * (W * 0.6 if dx >= 0 else -W * 0.6)
        if dx == 0:
            x = L.cx
        y = jy + fl + ((1 - k) * 260 if dx == 0 else 0) + (18 if dx else -10)
        product(c, name, x, y, jw * (1.12 if dx == 0 else 1), jh * (1.12 if dx == 0 else 1), k, 1, rot)
    # GRATIS stamp on the centre one
    s = back(t, 2.1, 0.55)
    if s > 0:
        st = pill("¡GRATIS!", "Anton.ttf", 58, RED, WHITE, 0.6, 0.3, outline=WHITE)
        put(c, st, L.cx + W * 0.11, jy - jh * 0.42, min(1, s * 1.5), max(0.2, s), -8)
    # price math
    a = ease(t, 3.0)
    old = text("$2,400", "Anton.ttf", 64, GREY, 0.02, strike=RED)
    new = text("$1,600", "Anton.ttf", 112, WHITE, 0.02)
    lab = text("3 JERSEYS POR", "MontB.ttf", 30, WHITE, 0.12)
    py = L.y(0.76 if L.story else 0.77)
    put(c, lab, L.cx, py - 78, a)
    put(c, old, L.cx - new.width / 2 - old.width / 2 - 6, py + 10 + (1 - a) * 30, a)
    put(c, new, L.cx + old.width / 2 - 6, py + (1 - a) * 30, a)
    a2 = ease(t, 3.7)
    sub = rich((("o 5 por $2,400 con el código ", WHITE), ("5X3", RED)), "Inter-SemiBold.otf", 30)
    put(c, sub, L.cx, py + 82, a2)
    footer(c, L, t, 4.3)
    return c


def lado(W, H, t):
    """Elige tu lado: América 110 vs Chivas — rivalidad local (lo que más mueve Bart Jerseys en MX)."""
    L = Frame(W, H)
    c = background(W, H, ((0.18, 0.5, 0.55, (210, 170, 40), 0.45), (0.82, 0.5, 0.55, RED, 0.5))).copy()
    # diagonal split line
    d = ImageDraw.Draw(c)
    k = ease(t, 0.2, 0.6)
    ytop, ybot = L.y(0.27), L.y(0.78)
    d.line([(W / 2 + 70, ytop), (W / 2 - 70 * (2 * k - 1), ytop + (ybot - ytop) * k)], fill=WHITE + (90,), width=4)
    head(c, L)
    h = text("ELIGE TU LADO", "Anton.ttf", 132 if L.story else 116, WHITE, 0.01)
    put(c, h, L.cx, L.y(0.07) + 28, 1)
    q = rich((("¿Águila ", (240, 205, 80)), ("o ", WHITE), ("Chiva?", (255, 80, 90))), "Inter-Bold.otf", 44)
    put(c, q, L.cx, L.y(0.07) + 28 + h.height * 0.78, ease(t, 0.15) if t < 1 else 1)
    jy, jh, jw = L.y(0.47), H * (0.30 if L.story else 0.33), W * 0.47
    a1, a2 = ease(t, 0.3, 0.6), ease(t, 0.6, 0.6)
    fl = lambda ph: math.sin(t * 1.5 + ph) * 7 if t > 1.2 else 0
    product(c, "america110.png", W * 0.26 - (1 - a1) * W * 0.5, jy + fl(0), jw, jh, a1, 1, -4)
    product(c, "chivas3.png", W * 0.74 + (1 - a2) * W * 0.5, jy + fl(2), jw, jh, a2, 1, 4)
    vs = back(t, 1.1, 0.5)
    if vs > 0:
        r = 74
        badge = Image.new("RGBA", (2 * r + 8, 2 * r + 8), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.ellipse([4, 4, 2 * r + 4, 2 * r + 4], fill=INK, outline=WHITE, width=5)
        tv = text("VS", "Anton.ttf", 70, WHITE)
        badge.alpha_composite(tv, ((badge.width - tv.width) // 2, (badge.height - tv.height) // 2))
        put(c, badge, L.cx, jy, min(1, vs * 1.4), max(0.3, vs))
    ln = L.y(0.69)
    a3 = ease(t, 1.6)
    put(c, text("AMÉRICA 110 AÑOS", "MontB.ttf", 30, (240, 205, 80), 0.1), W * 0.26, ln, a3)
    put(c, text("CHIVAS TERCERA 26/27", "MontB.ttf", 30, (255, 90, 100), 0.1), W * 0.74, ln, a3)
    a4 = ease(t, 2.2)
    p = rich((("$800 c/u  ·  ", WHITE), ("3x2", RED), (" en toda la tienda", WHITE)), "Inter-Bold.otf", 36)
    put(c, p, L.cx, ln + 70, a4)
    footer(c, L, t, 2.8)
    return c


def tacos(W, H, t):
    """Tacos F50 ROSE (producto #1 en ventas): gancho de precio y descuento de 40%."""
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.5, 0.6, (230, 70, 140), 0.42), (0.5, 0.85, 0.5, RED, 0.25))).copy()
    head(c, L)
    hook1 = text("¿$3,000 POR", "Anton.ttf", 120 if L.story else 104, WHITE, 0.01)
    hook2 = text("UNOS TACOS?", "Anton.ttf", 120 if L.story else 104, WHITE, 0.01)
    y0 = L.y(0.07) + 30
    flip = ease(t, 1.7, 0.4)
    put(c, hook1, L.cx, y0, 1 - flip)
    put(c, hook2, L.cx, y0 + hook1.height * 0.92, 1 - flip)
    n1 = rich((("NO. ", RED), ("$1,800", WHITE)), "Anton.ttf", 150 if L.story else 128)
    n2 = text("Y CON ENVÍO GRATIS", "MontB.ttf", 38, WHITE, 0.1)
    put(c, n1, L.cx, y0 + 30 - (1 - flip) * 30, flip)
    put(c, n2, L.cx, y0 + 30 + n1.height * 0.72, ease(t, 2.0))
    # boots: slow push-in
    zoom = 0.94 + 0.08 * min(1, t / 10)
    by = L.y(0.47 if L.story else 0.48)
    bw, bh = W * 0.98, H * (0.28 if L.story else 0.34)
    product(c, "f50rose1.png", L.cx, by + math.sin(t * 1.3) * 6, bw, bh, 1, zoom, 0)
    # -40% badge
    b = back(t, 2.4, 0.5)
    if b > 0:
        r = 92
        bd = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
        ImageDraw.Draw(bd).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=RED)
        tt = text("-40%", "Anton.ttf", 70, WHITE)
        bd.alpha_composite(tt, ((bd.width - tt.width) // 2, (bd.height - tt.height) // 2))
        put(c, bd, W * 0.80, by - bh * 0.42, min(1, b * 1.4), max(0.3, b), 10)
    a = ease(t, 3.0)
    nm = text("F50 ELITE · LAMINE YAMAL PACK ROSE", "MontB.ttf", 32, WHITE, 0.08)
    yy = L.y(0.76 if L.story else 0.745)
    put(c, nm, L.cx, yy, a)
    old = text("ANTES $3,000", "Inter-SemiBold.otf", 32, GREY, 0, strike=RED)
    put(c, old, L.cx, yy + 54, ease(t, 3.3))
    footer(c, L, t, 3.8, items=("Envío gratis", "Rastreo", "Stock limitado"))
    return c


RETRO = [("zidane98.png", "1998", "FRANCIA · ZIDANE 10"),
         ("arg06.png", "2006", "ARGENTINA · MESSI 19"),
         ("kaka.png", "2007", "MILAN · KAKÁ 22"),
         ("mu0708.png", "2008", "UNITED · MANGA LARGA")]


def retro(W, H, t):
    """Leyendas retro: un jersey por año (carrusel), luego la rejilla con RETRO10."""
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.5, 0.6, RED, 0.40),)).copy()
    c.alpha_composite(stripes(W, H, alpha=8))
    head(c, L)
    ttl = text("LEYENDAS RETRO", "Anton.ttf", 120 if L.story else 104, WHITE, 0.01)
    put(c, ttl, L.cx, L.y(0.07) + 30, 1)
    seq_end = 1.2 * len(RETRO)
    g = ease(t, seq_end, 0.6)
    jy = L.y(0.43 if L.story else 0.42)
    if g < 1:  # carousel: one legend at a time with a big year behind it
        i = min(len(RETRO) - 1, int(t / 1.2))
        lt = t - i * 1.2
        name, year, cap = RETRO[i]
        k = (1.0 if i == 0 else ease(lt, 0, 0.25)) * (1 - g)
        yr = text(year, "Anton.ttf", 400 if L.story else 340, (255, 255, 255, 34))
        put(c, yr, L.cx, jy - 10, k)
        product(c, name, L.cx + (0 if i == 0 else (1 - ease(lt, 0, 0.35)) * 140), jy, W * 0.62, H * (0.33 if L.story else 0.36), k)
        put(c, text(cap, "MontB.ttf", 34, WHITE, 0.12), L.cx, L.y(0.71), k)
    if g > 0:  # final grid
        gw, gh = W * 0.42, H * (0.155 if L.story else 0.185)
        for j, (name, year, cap) in enumerate(RETRO):
            gx = L.cx + (-1 if j % 2 == 0 else 1) * W * 0.215
            gy = jy + (-1 if j < 2 else 1) * gh * 0.56
            product(c, name, gx, gy + (1 - g) * 40, gw, gh, g)
            put(c, text(year, "Anton.ttf", 38, WHITE, 0.04), gx, gy + gh * 0.52, g)
    a = ease(t, seq_end + 0.3)
    off = rich((("10% OFF", RED), (" EN RETRO", WHITE)), "Anton.ttf", 92 if L.story else 80)
    code = pill("CÓDIGO: RETRO10", "Anton.ttf", 46, (0, 0, 0, 0), WHITE, 0.7, 0.32, outline=WHITE, track=0.06)
    yy = L.y(0.765 if L.story else 0.755)
    put(c, off, L.cx, yy - 30, a)
    put(c, code, L.cx, yy + off.height * 0.78, ease(t, seq_end + 0.5))
    footer(c, L, t, seq_end + 0.8, items=("Envío gratis", "Tallas S a 4XL", "Manga larga y corta"))
    return c


def card(name, w, h, rot=0, border=14):
    """Polaroid-style frame around a real customer photo."""
    im = Image.open(SRC + name).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((x, y, x + w, y + h))
    fr = Image.new("RGBA", (w + 2 * border, h + 2 * border), WHITE + (255,))
    fr.paste(im, (border, border))
    pad = 40
    out = Image.new("RGBA", (fr.width + 2 * pad, fr.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad + 6, pad + 12, pad + fr.width + 6, pad + fr.height + 12], fill=(0, 0, 0, 170))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    out.alpha_composite(fr, (pad, pad))
    return out.rotate(rot, Image.BICUBIC, expand=True) if rot else out


REVIEWS_TOP = ["review_201923.jpg", "review_213636.jpg", "review_201928.jpg"]
REVIEWS_DM = ["review_213712.jpg", "review_213652.jpg"]


@lru_cache(16)
def cards(rowh):
    h = int(rowh * 0.92)
    top = [card(n, int(h * (1.05 if i == 1 else 0.78)), h, r) for i, (n, r) in enumerate(zip(REVIEWS_TOP, (5, -3, -6)))]
    dm = [card(n, int(h * 0.86), h, r, 10) for n, r in zip(REVIEWS_DM, (-4, 4))]
    return top, dm


def resenas(W, H, t):
    """Prueba social con fotos y mensajes REALES de clientes (no inventados)."""
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.5, 0.6, RED, 0.35),)).copy()
    head(c, L)
    h1 = text("+3,000 PEDIDOS", "Anton.ttf", 128 if L.story else 108, WHITE, 0.01)
    h2 = rich((("ENTREGADOS ", WHITE), ("EN MÉXICO", RED)), "Anton.ttf", 76 if L.story else 64)
    y0 = L.y(0.07) + 30
    put(c, h1, L.cx, y0, 1)
    y2 = y0 + h1.height * 0.82
    put(c, h2, L.cx, y2, 1)
    st = stars(46)
    yy = L.y(0.80 if L.story else 0.81)
    r0, r1 = y2 + h2.height / 2 + 10, yy - 34 - st.height / 2 - 10
    rowh = int((r1 - r0) / 2)
    top, dm = cards(rowh)
    slots = [(top[0], 0.20, 0), (top[1], 0.50, 0), (top[2], 0.80, 0), (dm[0], 0.29, 1), (dm[1], 0.71, 1)]
    for j, (cd, px, row) in enumerate(slots):
        k = back(t, 0.4 + j * 0.45, 0.5)
        put(c, cd, W * px, r0 + rowh * (row + 0.5), min(1, k * 1.5), 0.8 + 0.2 * min(1, k))
    a = ease(t, 2.9)
    put(c, st, L.cx, yy - 34, a)
    put(c, text("Fotos y mensajes reales de nuestros clientes", "Inter-SemiBold.otf", 30, WHITE), L.cx, yy + 22, a)
    footer(c, L, t, 3.3, label="ARMA TU PEDIDO", items=("Envío gratis", "Rastreo", "Atención por WhatsApp"))
    return c


def urgencia(W, H, t):
    """Últimos días del 3x2 (termina el 31 de octubre)."""
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.42, 0.7, RED, 0.62),)).copy()
    c.alpha_composite(stripes(W, H, alpha=12))
    head(c, L)
    blink = 0.65 + 0.35 * (0.5 + 0.5 * math.sin(t * 6)) if t < 99 else 1
    tag = pill("ÚLTIMOS DÍAS", "Anton.ttf", 54, WHITE, RED, 0.7, 0.3, track=0.06)
    put(c, tag, L.cx, L.top + 95, blink if t < 99 else 1)
    big = text("3X2", "Anton.ttf", 330 if L.story else 260, WHITE, 0.0)
    put(c, big, L.cx, L.y(0.24), 1, 1 + 0.02 * math.sin(t * 3))
    put(c, text("EN TODAS LAS JERSEYS", "MontB.ttf", 40, WHITE, 0.14), L.cx, L.y(0.38), 1)
    jy, jh, jw = L.y(0.565), H * (0.20 if L.story else 0.22), W * 0.34
    for j, (name, dx, rot) in enumerate([("psg4.png", -0.30, -9), ("rm_away.png", 0.30, 9), ("arg_last.png", 0, 0)]):
        k = ease(t, 0.3 + j * 0.25)
        product(c, name, L.cx + dx * W, jy + (14 if dx else -6) + (1 - k) * 80, jw * (1.1 if not dx else 1), jh * (1.1 if not dx else 1), k, 1, rot)
    a = ease(t, 1.4)
    put(c, rich((("TERMINA EL ", WHITE), ("31 DE OCTUBRE", RED)), "Anton.ttf", 70 if L.story else 60), L.cx, L.y(0.745 if L.story else 0.735), a)
    footer(c, L, t, 1.8, label="APROVECHA AHORA")
    return c


def regreso(W, H, t):
    """Retargeting (visitó / agregó al carrito y no compró)."""
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.5, 0.6, RED, 0.40),)).copy()
    head(c, L)
    h1 = text("¿SE TE OLVIDÓ", "Anton.ttf", 124 if L.story else 104, WHITE, 0.01)
    h2 = rich((("ALGO", WHITE), ("?", RED)), "Anton.ttf", 124 if L.story else 104)
    y0 = L.y(0.07) + 30
    put(c, h1, L.cx, y0, 1)
    put(c, h2, L.cx, y0 + h1.height * 0.9, 1)
    # cart card
    k = ease(t, 0.3, 0.6)
    cw, ch = int(W * (0.70 if L.story else 0.72)), int(H * (0.32 if L.story else 0.36))
    cardim = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(cardim)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=28, fill=(18, 18, 20, 255), outline=(255, 255, 255, 40), width=2)
    ph = Image.open(SRC + "barca_black.jpg").convert("RGB")
    pw = cw - 48
    phh = int(ch * 0.70)
    s = max(pw / ph.width, phh / ph.height)
    ph = ph.resize((round(ph.width * s), round(ph.height * s)), Image.LANCZOS)
    ph = ph.crop(((ph.width - pw) // 2, int((ph.height - phh) * 0.4), (ph.width - pw) // 2 + pw, int((ph.height - phh) * 0.4) + phh))
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], radius=18, fill=255)
    cardim.paste(ph, (24, 24), m)
    tl = text("Barcelona Black Special Edition", "Inter-Bold.otf", 34, WHITE)
    cardim.alpha_composite(tl, (24, 24 + phh + 14))
    pr = rich((("$800  ", WHITE), ("$1,100", GREY)), "Inter-Bold.otf", 34)
    cardim.alpha_composite(pr, (24, 24 + phh + 14 + tl.height + 4))
    sl = text("$1,100", "Inter-Bold.otf", 34, GREY, strike=RED)
    cardim.alpha_composite(sl, (24 + pr.width - sl.width, 24 + phh + 14 + tl.height + 4))
    put(c, cardim, L.cx, L.y(0.515 if L.story else 0.50) + (1 - k) * 60, k, 1, -2 * (1 - k))
    a = ease(t, 1.0)
    ty = L.y(0.775 if L.story else 0.735)
    put(c, text("Tu jersey sigue esperándote", "Inter-Bold.otf", 44, WHITE), L.cx, ty, a)
    put(c, rich((("Envío gratis + ", GREY), ("3x2", RED), (" en toda la tienda", GREY)), "Inter-SemiBold.otf", 32), L.cx, ty + 52, ease(t, 1.3))
    footer(c, L, t, 1.7, label="TERMINAR MI COMPRA", items=("Pago seguro", "Rastreo", "Garantía de entrega"))
    return c


CONCEPTS = {
    "trio": (trio, 11), "lado": (lado, 10), "tacos": (tacos, 10), "retro": (retro, 12),
    "resenas": (resenas, 10), "urgencia": (urgencia, 8), "regreso": (regreso, 8),
}


# ---------------------------------------------------------------- output

def still(name, size):
    fn, _ = CONCEPTS[name]
    W, H = size
    im = fn(W, H, 99).convert("RGB")
    tag = "feed-1080x1350" if H < 1500 else "historia-1080x1920"
    path = f"{OUT}{name}-{tag}.jpg"
    im.save(path, quality=93, subsampling=0)
    return path


def video(name, size):
    fn, dur = CONCEPTS[name]
    W, H = size
    tag = "feed-1080x1350" if H < 1500 else "historia-1080x1920"
    path = f"{OUT}{name}-{tag}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS
        p.stdin.write(fn(W, H, t).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = args or list(CONCEPTS)
    for n in names:
        for sz in (FEED, STORY):
            print(still(n, sz))
    if "--video" in sys.argv:
        for n in names:
            for sz in (STORY, FEED):
                print(video(n, sz))
