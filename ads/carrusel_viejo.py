"""Carrusel meme 'Lo que le pedí a mi viejo / Lo que me trajo' (1080x1350): jersey actual vs. su versión retro.

Fondo gris carbón, jersey a la izquierda, texto Poppins Bold apretado a la derecha, logo abajo al centro.
Todas las jerseys están en la tienda; el último slide lo remata ("spoiler: las dos están en la tienda").
Uso: python3 carrusel_viejo.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import generar_ads as g
from generar_ads import put
from hf_ads import badge

SRC = g.HERE + "src/"
OUT = g.HERE + "out/viejo/"
W, H = 1080, 1350
BG, WHITE, SOFT, RED = (35, 35, 37), (255, 255, 255), (170, 170, 176), (225, 30, 45)
FONT = g.HERE + "fonts/Poppins-Bold.ttf"

PAIRS = [
    ("viejo/rm_away_2627.png", "viejo/rm1213.png"),
    ("spotify/golf.png", "viejo/fcb0506.png"),
    ("spotify/travis_fan_v2.png", "viejo/fcb0809.png"),
    ("outfit/america.png", "viejo/ame1213.png"),
]


def tight(s, px, fill=WHITE, track=-0.045):
    """Poppins Bold with negative tracking, like the reference meme."""
    f = ImageFont.truetype(FONT, int(px))
    bb = f.getbbox(s)
    w = sum(f.getlength(c) for c in s) + track * px * (len(s) - 1)
    im = Image.new("RGBA", (int(w) + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 10
    for c in s:
        d.text((x, 10 - bb[1]), c, font=f, fill=fill)
        x += f.getlength(c) + track * px
    return im


def block(c, lines, x, y, px=66, gap=1.0):
    """Left-aligned multi-line text with its first line's top at y."""
    for i, s in enumerate(lines):
        t = tight(s, px)
        c.alpha_composite(t, (int(x), int(y + i * px * gap)))


def jersey(name, h):
    im = Image.open(SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    s = min(h / im.height, 470 / im.width)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    p = 40
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p, p + 10))
    a = a.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.5))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out


def slide(new, old):
    c = Image.new("RGBA", (W, H), BG + (255,))
    put(c, jersey(new, 480), 300, 380)
    put(c, jersey(old, 480), 300, 920)
    block(c, ["Lo que le pedí a", "mi viejo"], 560, 310)
    block(c, ["Lo que", "me trajo"], 560, 860)
    put(c, badge(110), W / 2, H - 85)
    return c


def cierre():
    c = Image.new("RGBA", (W, H), BG + (255,))
    block(c, ["Spoiler:", "las dos están", "en la tienda."], 110, 300, px=104)
    put(c, tight("3 JERSEYS POR $1,600  ·  ENVÍO GRATIS", 40, RED, 0.0), W / 2, 760)
    put(c, tight("Pídele a tu viejo la correcta.", 44, SOFT, -0.02), W / 2, 850)
    put(c, tight("Haz tu pedido por DM o en footballfrenzy.shop", 38, WHITE, -0.02), W / 2, 930)
    put(c, badge(170), W / 2, H - 200)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [lambda p=p: slide(*p) for p in PAIRS] + [cierre]
    for n, fn in enumerate(slides, 1):
        fn().convert("RGB").save(f"{OUT}{n:02d}.jpg", quality=93, subsampling=0)
    print(len(slides), "slides")
