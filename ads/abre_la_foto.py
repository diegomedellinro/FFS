"""Carrusel trend "ABRE LA FOTO" con la estética de la marca (logo Football Frenzy Shop):
negro profundo, letra brush blanca con glow neón rojo, trazos de pincel rojos, corona y caja blanca tipo "SHOP".

1) Abre la foto  →  2) Me debes una jersey para el Clásico (Madrid y Barça)  →  3) Pídela por DM o en la web.
Formato 1080x1350 (4:5). Uso: python3 abre_la_foto.py
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import generar_ads as g
from generar_ads import text, put, WHITE, INK

W, H = 1080, 1350
OUT = g.HERE + "out/abre_la_foto/"
NEON = (255, 30, 45)
SCRIPT = "MrDafoe-Regular.ttf"
WA_GREEN = (37, 160, 90)


# ---------------------------------------------------------------- brand helpers

def neon(layer, color=NEON, r=(10, 28), k=(1.4, 0.9), drop=(5, 7)):
    """Wrap a white layer in a red neon glow + a red offset edge underneath, like the logo lettering."""
    p = r[1] * 3
    out = Image.new("RGBA", (layer.width + 2 * p, layer.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(layer.getchannel("A"), (p, p))
    for rad, kk in zip(r, k):
        gl = a.filter(ImageFilter.GaussianBlur(rad)).point(lambda v, kk=kk: min(255, int(v * kk)))
        out.alpha_composite(Image.composite(Image.new("RGBA", out.size, color + (255,)), Image.new("RGBA", out.size, (0, 0, 0, 0)), gl))
    edge = Image.new("RGBA", out.size, (0, 0, 0, 0))
    edge.paste(Image.new("RGBA", layer.size, color + (255,)), (p + drop[0], p + drop[1]), layer.getchannel("A"))
    out.alpha_composite(edge)
    out.alpha_composite(layer, (p, p))
    return out


def script(s, px, rot=7):
    """White brush-script line with neon, tilted up like the logo."""
    lay = text(s, SCRIPT, px, (246, 246, 246))
    lay = lay.rotate(rot, Image.BICUBIC, expand=True)
    return neon(lay)


def brush(w, h=22, seed=1, color=NEON):
    """Tapered red brush stroke with dry-brush streaks + glow."""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w + 80, h * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cy = im.height / 2
    for i in range(14):
        off = rnd.uniform(-h * 0.45, h * 0.45)
        th = rnd.uniform(2, h * 0.35)
        x0 = 40 + rnd.uniform(0, w * 0.18)
        x1 = 40 + w - rnd.uniform(0, w * 0.12)
        pts = [(x0, cy + off), (x1, cy + off - th * 0.3), (x1, cy + off + th * 0.2), (x0 + w * 0.08, cy + off + th)]
        d.polygon(pts, fill=color + (rnd.randint(170, 255),))
    # main tapered body
    d.polygon([(40, cy + 2), (40 + w * 0.15, cy - h * 0.35), (40 + w, cy - h * 0.15), (40 + w * 0.9, cy + h * 0.3), (40 + w * 0.12, cy + h * 0.2)], fill=color + (255,))
    glow = im.filter(ImageFilter.GaussianBlur(12))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(glow)
    out.alpha_composite(im)
    return out


def crown(w):
    """Red neon crown outline like the logo's."""
    h = int(w * 0.62)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(5, w // 16)
    pts = [(w * .08, h * .3), (w * .3, h * .62), (w * .5, h * .08), (w * .7, h * .62), (w * .92, h * .3), (w * .82, h * .9), (w * .18, h * .9), (w * .08, h * .3)]
    d.line(pts, fill=(255, 70, 80, 255), width=lw, joint="curve")
    return neon(im, r=(8, 20), k=(1.6, 1.0), drop=(0, 0))


def shop_box(s, px=40, padx=1.1, pady=0.55, track=0.35):
    """White box with spaced black caps + red glow (the 'SHOP' plate), flanked by red lines."""
    t = text(s, "MontB.ttf", px, INK, track)
    w, h = int(t.width + px * padx * 2), int(t.height + px * pady * 2)
    box = Image.new("RGBA", (w, h), (244, 244, 244, 255))
    box.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    lw = int(px * 2.6)
    full = Image.new("RGBA", (w + 2 * (lw + 24), h), (0, 0, 0, 0))
    d = ImageDraw.Draw(full)
    for x0 in (0, w + lw + 48):
        d.line([(x0, h / 2), (x0 + lw, h / 2)], fill=NEON + (255,), width=4)
    full.alpha_composite(box, (lw + 24, 0))
    return neon(full, r=(6, 18), k=(1.2, 0.8), drop=(0, 0))


def caps(s, px, color=WHITE, track=0.18):
    return text(s, "MontB.ttf", px, color, track)


_BG = {}


def bg(glows=((0.5, 0.42, 0.75, 0.30),)):
    """Near-black with soft red bloom, vignette and grain."""
    key = glows
    if key not in _BG:
        _BG[key] = g.background(W, H, tuple((x, y, r, (150, 10, 20), k) for x, y, r, k in glows), base=(6, 6, 7))
    return _BG[key].copy()


LOGO = None


def logo(w):
    """The real logo (black background) as a screen-blend layer."""
    global LOGO
    if LOGO is None:
        LOGO = Image.open(g.SRC + "logo_ff.png").convert("RGB")
    im = LOGO.resize((w, w), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32)
    a = np.clip(arr.max(axis=2) * 1.6, 0, 255).astype(np.uint8)
    lay = Image.fromarray(np.dstack([arr.astype(np.uint8), a]), "RGBA")
    return lay


def sign(c, y=H - 92, w=190):
    put(c, logo(w), W / 2, y)


# ---------------------------------------------------------------- pieces

def bubble(s=1.0):
    """WhatsApp 'view once' photo message with a red neon halo."""
    w, h, tail = int(560 * s), int(200 * s), int(46 * s)
    im = Image.new("RGBA", (w + tail + 10, h + 10), (0, 0, 0, 0))
    ox, oy = tail, 0
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([ox, oy, ox + w, oy + h], radius=int(52 * s), fill=(250, 250, 250, 255))
    d.polygon([(ox + 40 * s, oy + h - 70 * s), (ox - tail * 0.8, oy + h + 6 * s), (ox + 100 * s, oy + h - 8 * s)], fill=(250, 250, 250, 255))
    cx, cy, r = ox + 110 * s, oy + h * 0.44, 42 * s
    lw = max(4, int(7 * s))
    d.arc([cx - r, cy - r, cx + r, cy + r], -60, 200, fill=WA_GREEN, width=lw)
    for st in (214, 240, 266):
        d.arc([cx - r, cy - r, cx + r, cy + r], st, st + 12, fill=WA_GREEN, width=lw)
    one = text("1", "Inter-SemiBold.otf", int(46 * s), WA_GREEN)
    im.alpha_composite(one, (int(cx - one.width / 2), int(cy - one.height / 2)))
    foto = text("Foto", "Inter-SemiBold.otf", int(70 * s), (30, 30, 34))
    im.alpha_composite(foto, (int(cx + r + 34 * s), int(cy - foto.height / 2)))
    hr = text("10:37", "Inter-SemiBold.otf", int(44 * s), (110, 110, 116))
    im.alpha_composite(hr, (int(ox + w - hr.width - 34 * s), int(oy + h - hr.height - 18 * s)))
    return neon(im, r=(14, 40), k=(0.9, 0.7), drop=(0, 0))


def jersey_glow(c, name, cx, cy, w, h, rot):
    """Product with a red rim-light behind it."""
    lay = g.with_shadow(name, int(w), int(h))
    a = lay.getchannel("A").filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, int(v * 1.3)))
    glow = Image.composite(Image.new("RGBA", lay.size, NEON + (255,)), Image.new("RGBA", lay.size, (0, 0, 0, 0)), a)
    put(c, glow, cx, cy, 0.85, 1.04, rot)
    put(c, lay, cx, cy, 1, 1, rot)


def option(icon, title, sub, w=900, h=180):
    """Black card with neon red border."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=(12, 12, 14, 255), outline=(255, 60, 70, 255), width=4)
    im.alpha_composite(icon, (int(90 - icon.width / 2), int(h / 2 - icon.height / 2)))
    t1 = text(title, "Anton.ttf", 58, WHITE, 0.02)
    t2 = text(sub, "Inter-SemiBold.otf", 32, (175, 175, 182))
    im.alpha_composite(t1, (170, int(h / 2 - t1.height + 4)))
    im.alpha_composite(t2, (172, int(h / 2 + 10)))
    return neon(im, r=(10, 26), k=(0.7, 0.5), drop=(0, 0))


def plane(px, color=(255, 60, 70)):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(5, px // 11)
    a, b, cc = (px * 0.08, px * 0.12), (px * 0.92, px * 0.12), (px * 0.55, px * 0.9)
    d.line([a, b, cc, (px * 0.42, px * 0.42), a], fill=color, width=lw, joint="curve")
    d.line([(px * 0.42, px * 0.42), b], fill=color, width=lw)
    return im


def globe(px, color=(255, 60, 70)):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(5, px // 12)
    m = lw
    d.ellipse([m, m, px - m, px - m], outline=color, width=lw)
    d.ellipse([px * 0.3, m, px * 0.7, px - m], outline=color, width=lw)
    d.line([(m, px / 2), (px - m, px / 2)], fill=color, width=lw)
    return im


# ---------------------------------------------------------------- slides

def slide1():
    c = bg(((0.5, 0.45, 0.8, 0.32),))
    put(c, crown(170), W / 2 + 40, 175)
    put(c, brush(700, 20, 3), W / 2 - 20, 300, 0.9, 1, 7)
    put(c, script("Abre", 300), W / 2 - 40, 345)
    put(c, script("la foto", 270), W / 2 + 30, 560)
    put(c, brush(760, 24, 5), W / 2 + 10, 700, 1, 1, 6)
    put(c, bubble(1.0), W / 2 - 10, 935)
    sign(c)
    return c


def slide2():
    c = bg(((0.5, 0.58, 0.7, 0.34),))
    put(c, script("Me debes una jersey", 150, 5), W / 2, 170)
    put(c, shop_box("PARA EL CLÁSICO", 44), W / 2, 330)
    jersey_glow(c, "rm125.png", W * 0.285, 720, 500, 560, -7)
    jersey_glow(c, "barca_away.png", W * 0.715, 740, 500, 560, 7)
    put(c, neon(text("VS", "Anton.ttf", 120, WHITE)), W / 2, 715)
    put(c, brush(860, 18, 9), W / 2, 1000, 1, 1, 3)
    put(c, caps("REAL MADRID", 34), W * 0.285, 1060)
    put(c, caps("BARÇA", 34), W * 0.715, 1060)
    put(c, text("Etiqueta a quien te la debe", "Inter-Bold.otf", 42, (230, 230, 235)), W / 2, 1150)
    sign(c, w=170)
    return c


def slide3():
    c = bg(((0.5, 0.4, 0.75, 0.3),))
    put(c, crown(130), W / 2 + 60, 105)
    put(c, script("Pídela", 260), W / 2, 250)
    put(c, shop_box("ANTES DEL CLÁSICO", 40), W / 2, 420)
    put(c, option(plane(72), "POR MENSAJE DIRECTO", "Escríbenos por DM y te ayudamos"), W / 2, 590)
    put(c, script("o", 110, 0), W / 2, 718)
    put(c, option(globe(74), "EN FOOTBALLFRENZY.SHOP", "Elige talla, versión y dorsal"), W / 2, 850)
    put(c, g.rich((("LLEVA 3, ", WHITE), ("PAGA 2", NEON)), "Anton.ttf", 78), W / 2, 1020)
    put(c, caps("ENVÍO GRATIS  ·  TALLAS S A 4XL  ·  PAGO SEGURO", 24, (200, 200, 206), 0.14), W / 2, 1090)
    sign(c, w=170)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i, fn in enumerate((slide1, slide2, slide3), 1):
        fn().convert("RGB").save(f"{OUT}{i}-{fn.__name__}.jpg", quality=93, subsampling=0)
    print("ok")
