"""Carrusel 'Jerseys Retro' (1080x1350) con la estética editorial del ad retro (serif Playfair + itálica).

Portada (foto) → 5 jerseys retro reales de la tienda → cómo funciona el 3x2 → cierre con CTA (foto).
Uso: python3 carrusel_retro.py
"""
import os
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put
from hf_ads import gradient
from barca_golf import serif, caps, lockup, base, compose, ITAL

OUT = g.HERE + "out/carrusel_retro/"
PHOTO = g.HERE + "out/hf_ads/raw/retro-outpaint.png"
W, H = 1080, 1350
ERODE = {"cl_fcb_1415.png"}
SOFT = (215, 215, 220)
GOLD = (214, 182, 118)

JERSEYS = [
    ("cl_rm_1112.png", "TEMPORADA 11/12", "REAL MADRID", "La de los 100 puntos"),
    ("cl_rm_1718ls.png", "TEMPORADA 17/18", "REAL MADRID", "Kiev y la tercera Champions seguida"),
    ("cl_fcb_0809.png", "TEMPORADA 08/09", "FC BARCELONA", "El primer triplete"),
    ("cl_fcb_1415.png", "TEMPORADA 14/15", "FC BARCELONA", "Messi, Suárez y Neymar"),
    ("zidane98.png", "MUNDIAL 1998", "FRANCIA", "Zidane y la primera estrella"),
]


def backdrop():
    """The retro photo, blurred and darkened: same mood as the cover, quiet enough for a product."""
    im = Image.open(PHOTO).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS).crop((0, 300, W, 300 + H))
    im = im.filter(ImageFilter.GaussianBlur(28)).convert("RGBA")
    im.alpha_composite(Image.new("RGBA", (W, H), (8, 8, 10, 175)))
    return im


def fade(c, y0, y1, k=0.85):
    """Dark band: transparent above y0, ramps to k by y1, solid below."""
    a = np.zeros((H, W), np.float32)
    a[y0:y1] = np.linspace(0, k, y1 - y0)[:, None] ** 1.3
    a[y1:] = k
    m = Image.fromarray((a * 255).astype(np.uint8))
    c.alpha_composite(Image.composite(Image.new("RGBA", (W, H), (6, 6, 8, 255)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), m))


def counter(c, n, total):
    put(c, caps(f"{n:02d} / {total:02d}", 20, 0.3, SOFT), W - 90, H - 50)


def jersey(name, h):
    im = Image.open(g.SRC + name).convert("RGBA")
    bb = im.getchannel("A").getbbox()
    im = im.crop(bb)
    if name in ERODE:
        a = np.asarray(im.getchannel("A").filter(ImageFilter.MinFilter(7)))
        lab, n = ndimage.label(a > 20)
        keep = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
        im.putalpha(Image.fromarray(np.where(keep, a, 0).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    if im.width > 760:
        im = im.resize((760, round(im.height * 760 / im.width)), Image.LANCZOS)
    p = 60
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p, p + 18))
    sh = a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.55))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), sh))
    out.alpha_composite(im, (p, p))
    return out


def rule(w):
    im = Image.new("RGBA", (w, 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).line([(0, 2), (w, 2)], fill=GOLD + (230,), width=2)
    return im


def cover():
    c = compose(W, H, 70, 1090, top_crop=0.02, src=PHOTO, title="JERSEYS", sub="Retro", title_px=150, logo=120)
    # replace the bottom CTA with a swipe hint: redraw the lower band
    low = base(W, H, 0.02, PHOTO).crop((0, 1020, W, H))
    c.alpha_composite(low, (0, 1020))
    fade(c, 1020, 1130, 0.82)
    put(c, serif("Cinco camisetas que hicieron historia", 42, ITAL), W / 2, 1170)
    put(c, caps("DESLIZA  >>", 24, 0.4), W / 2, 1250)
    return c


def slide(i, name, kick, club, line):
    c = backdrop()
    put(c, caps(kick, 26, 0.45, GOLD), W / 2, 110)
    put(c, serif(club, 104 if len(club) < 12 else 92, track=0.01), W / 2, 200)
    put(c, serif(line, 44, ITAL, fill=SOFT), W / 2, 295)
    put(c, jersey(name, 700), W / 2, 745)
    put(c, rule(420), W / 2, 1160)
    put(c, caps("$800  ·  3 POR $1,600", 30, 0.3), W / 2, 1215)
    counter(c, i, 5)
    return c


def como():
    c = backdrop()
    put(c, caps("ASÍ FUNCIONA", 26, 0.45, GOLD), W / 2, 150)
    put(c, serif("3X2 ACTIVO", 120, track=0.01), W / 2, 260)
    put(c, serif("en todas las jerseys", 48, ITAL, fill=SOFT), W / 2, 365)
    steps = (("I", "Elige 3 jerseys", "Retro, temporada actual o selecciones"),
             ("II", "Paga solo 2", "El descuento se aplica solo en el carrito"),
             ("III", "Recíbelas en casa", "Envío gratis · tallas S a 4XL"))
    for k, (n, t, s) in enumerate(steps):
        y = 520 + k * 210
        put(c, serif(n, 64, fill=GOLD), 210, y + 10)
        put(c, serif(t, 54), 610, y - 18)
        put(c, text_small(s), 610, y + 48)
    put(c, rule(420), W / 2, 1180)
    put(c, caps("3 JERSEYS POR $1,600", 30, 0.3), W / 2, 1235)
    return c


def text_small(s):
    return g.text(s, "Inter-SemiBold.otf", 30, SOFT)


def cierre():
    c = base(W, H, 0.12, PHOTO)
    gradient(c, top=True, h=0.20, k=0.45)
    fade(c, 830, 960, 0.86)
    put(c, caps("3X2 ACTIVO", 28, 0.45, GOLD), W / 2, 960)
    put(c, serif("Haz tu pedido", 96), W / 2, 1045)
    put(c, serif("por mensaje directo o en el sitio web", 44, ITAL, fill=SOFT), W / 2, 1135)
    put(c, lockup(110), W / 2, 1255)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [cover] + [lambda i=i, j=j: slide(i, *j) for i, j in enumerate(JERSEYS, 1)] + [como, cierre]
    for n, fn in enumerate(slides, 1):
        fn().convert("RGB").save(f"{OUT}{n:02d}.jpg", quality=93, subsampling=0)
    print(len(slides), "slides")
