"""Promo '3X2 · 3 jerseys por $1,600' en historia (1080x1920) y post (1080x1350), sin IA de pago.

Fondo blanco con viñeta gris suave, logo arriba, "3X2" gigante en rojo, tres jerseys reales de la tienda en abanico
(la del centro al frente) con sombra de piso, y precio abajo.
Uso: python3 promo_3x2.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text, RED, INK
from hf_ads import badge

OUT = g.HERE + "out/promo3x2/"
TRIO = ("cl_fcb_home26.png", "barca_away.png", "cl_fcb_third26.png")   # izquierda, centro (al frente), derecha
GREY = (90, 90, 96)


def backdrop(W, H):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.5) / H) ** 2)
    v = 252 - 26 * r ** 2 + np.random.default_rng(2).normal(0, 0.8, (H, W))
    return Image.fromarray(np.dstack([v, v, v + 1]).clip(0, 255).astype(np.uint8)).convert("RGBA")


def jersey(name, h, rot):
    im = Image.open(g.SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    p = 70
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p + 10, p + 18))
    a = a.filter(ImageFilter.GaussianBlur(20)).point(lambda v: int(v * 0.30))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out.rotate(rot, Image.BICUBIC, expand=True)


def floor(c, cx, cy, w):
    sh = Image.new("L", c.size, 0)
    ImageDraw.Draw(sh).ellipse([cx - w / 2, cy - 22, cx + w / 2, cy + 22], fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    c.alpha_composite(Image.composite(Image.new("RGBA", c.size, (0, 0, 0, 255)), Image.new("RGBA", c.size, (0, 0, 0, 0)), sh))


def trio(c, cx, cy, h, spread=0.62):
    """Fan of three jerseys; the middle one is bigger and in front, like the reference."""
    floor(c, cx, cy + h * 0.62, h * 1.9)
    side = int(h * 0.88)
    put(c, jersey(TRIO[0], side, 9), cx - h * spread, cy - h * 0.04)
    put(c, jersey(TRIO[2], side, -9), cx + h * spread, cy - h * 0.04)
    put(c, jersey(TRIO[1], h, 0), cx, cy + h * 0.06)


def big(c, y, px):
    put(c, text("3X2", "Anton.ttf", px, RED, -0.01), c.width / 2, y)


def price(c, y, scale=1.0):
    put(c, text("3 JERSEYS POR", "Anton.ttf", int(78 * scale), INK, 0.01), c.width / 2, y)
    put(c, text("$1,600", "Anton.ttf", int(190 * scale), RED, 0.0), c.width / 2, y + 155 * scale)
    put(c, text("EN TODAS LAS JERSEYS", "MontB.ttf", int(32 * scale), INK, 0.32), c.width / 2, y + 290 * scale)


def post():
    c = backdrop(1080, 1350)
    put(c, badge(118), 540, 92)
    big(c, 320, 330)
    trio(c, 540, 690, 430)
    price(c, 1040, 0.86)
    return c


def story():
    c = backdrop(1080, 1920)
    put(c, badge(150), 540, 250)
    big(c, 560, 380)
    trio(c, 540, 1010, 450, 0.56)
    price(c, 1400, 1.0)
    put(c, text("HAZ TU PEDIDO POR DM O EN FOOTBALLFRENZY.SHOP", "MontB.ttf", 28, GREY, 0.06), 540, 1775)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    post().convert("RGB").save(OUT + "post-3x2.jpg", quality=94, subsampling=0)
    story().convert("RGB").save(OUT + "story-3x2.jpg", quality=94, subsampling=0)
    print("ok")
