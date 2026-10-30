"""Carrusel 'Jerseys que puedes encargar con nosotros' (1080x1350), inspirado en el formato de catálogo con grano.

Fondo rojo de marca con grano, título Poppins Bold en minúsculas + año en itálica (Playfair), jersey real de la
tienda al centro, logo con estrellas abajo. Portada con dos jerseys en semitono (halftone).
Uso: python3 carrusel_encargo.py
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import generar_ads as g
from generar_ads import put
from hf_ads import badge

SRC = g.HERE + "src/"
OUT = g.HERE + "out/encargo/"
W, H = 1080, 1350
RED = (178, 34, 40)
CREAM = (246, 236, 226)
WINE = (70, 12, 16)
POP = g.HERE + "fonts/Poppins-Bold.ttf"
ITAL = g.HERE + "fonts/PlayfairDisplay-MediumItalic.ttf"

JERSEYS = [
    ("outfit/america.png", "Club América Local", "2026/27"),
    ("encargo/chivas.png", "Chivas Local", "2026/27"),
    ("encargo/pumas.png", "Pumas Local", "2026/27"),
    ("encargo/cruzazul.png", "Cruz Azul Local", "2026/27"),
    ("encargo/tigres.png", "Tigres Local", "2026/27"),
    ("encargo/toluca99.png", "Toluca Local", "1999/00"),
    ("viejo/rm_away_2627.png", "Real Madrid Visitante", "2026/27"),
    ("rm_1112_home.png", "Real Madrid Local", "2011/12"),
    ("spotify/golf.png", "FC Barcelona x Golf", "2026/27"),
    ("viejo/fcb0809.png", "FC Barcelona Local", "2008/09"),
]


def font_text(s, path, px, fill=CREAM, track=-0.03):
    f = ImageFont.truetype(path, int(px))
    bb = f.getbbox(s)
    w = sum(f.getlength(c) for c in s) + track * px * (len(s) - 1)
    im = Image.new("RGBA", (int(w) + 30, bb[3] - bb[1] + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 15
    for c in s:
        d.text((x, 15 - bb[1]), c, font=f, fill=fill)
        x += f.getlength(c) + track * px
    return im


def grain_bg(color=RED):
    rng = np.random.default_rng(11)
    base = np.array(color, np.float32)[None, None, :]
    n = rng.normal(0, 9, (H, W, 1))
    speck = (rng.random((H, W, 1)) > 0.985) * rng.normal(0, 22, (H, W, 1))
    return Image.fromarray((base + n + speck).clip(0, 255).astype(np.uint8).repeat(1, 2)).convert("RGBA")


def grain(c, k=7):
    """Film grain over everything (text and jerseys too), like the reference."""
    n = np.random.default_rng(5).normal(0, k, (H, W, 1))
    a = np.asarray(c.convert("RGB"), np.float32) + n
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")


def star(r):
    im = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((r + rr * math.cos(a), r + rr * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=CREAM + (255,))
    return im


def brand_row(c, y, logo=120):
    put(c, badge(logo), W / 2, y)
    put(c, star(34), W / 2 - logo * 0.95, y)
    put(c, star(34), W / 2 + logo * 0.95, y)


def jersey(name, maxw=680, maxh=640):
    im = Image.open(SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    s = min(maxw / im.width, maxh / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    p = 60
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p, p + 22))
    a = a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.45))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (40, 5, 8, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out


def halftone(name, h, cell=11, ang=0.6):
    """Duotone halftone print of a jersey (wine dots on cream), keeping its silhouette."""
    im = Image.open(SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    gray = np.asarray(im.convert("L"), np.float32) / 255
    yy, xx = np.mgrid[0:im.height, 0:im.width].astype(np.float32)
    u = (xx * math.cos(ang) - yy * math.sin(ang)) * 2 * math.pi / cell
    v = (xx * math.sin(ang) + yy * math.cos(ang)) * 2 * math.pi / cell
    screen = (np.sin(u) * np.sin(v) + 1) / 2
    dark = gray < screen * 0.9 + 0.05
    rgb = np.where(dark[..., None], np.array(WINE, np.float32), np.array(CREAM, np.float32))
    out = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def cover():
    c = grain_bg()
    brand_row(c, 175, 150)
    for i, s in enumerate(["jerseys", "que puedes", "encargar"]):
        put(c, font_text(s, POP, 138), W / 2 + (-40, 0, 20)[i], 345 + i * 118)
    put(c, font_text("con nosotros", ITAL, 112, track=0.0), W / 2, 670)
    pill = font_text("desliza", POP, 54, RED)
    box = Image.new("RGBA", (pill.width + 30, pill.height + 6), CREAM + (255,))
    m = Image.new("L", box.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, box.width - 1, box.height - 1], radius=16, fill=255)
    box.putalpha(m)
    box.alpha_composite(pill, (15, 3))
    put(c, box, W / 2, 790)
    a = halftone("viejo/rm_away_2627.png", 620).rotate(8, Image.BICUBIC, expand=True)
    b = halftone("spotify/golf.png", 600).rotate(-10, Image.BICUBIC, expand=True)
    c.alpha_composite(b, (W - b.width + 140, 930))
    c.alpha_composite(a, (-150, 900))
    return grain(c)


def slide(name, title, year):
    c = grain_bg()
    size = 92 if len(title) <= 18 else 80
    put(c, font_text(title, POP, size), W / 2, 150)
    put(c, font_text(year, ITAL, 100, track=0.02), W / 2, 265)
    put(c, jersey(name), W / 2, 700)
    brand_row(c, 1225)
    return grain(c)


def cierre():
    c = grain_bg()
    brand_row(c, 230, 170)
    for i, s in enumerate(["encarga la", "tuya hoy"]):
        put(c, font_text(s, POP, 140), W / 2, 470 + i * 135)
    put(c, font_text("3 por $1,600 · envío gratis", ITAL, 70, track=0.0), W / 2, 750)
    put(c, font_text("mándanos DM o pide en footballfrenzy.shop", POP, 40, CREAM, -0.01), W / 2, 880)
    put(c, font_text("Liga MX · Real Madrid · Barça · retro y temporada 26/27", POP, 30, (240, 200, 195), 0.0), W / 2, 950)
    return grain(c)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [cover] + [lambda j=j: slide(*j) for j in JERSEYS] + [cierre]
    for n, fn in enumerate(slides, 1):
        fn().convert("RGB").save(f"{OUT}{n:02d}.jpg", quality=93, subsampling=0)
    print(len(slides), "slides")
