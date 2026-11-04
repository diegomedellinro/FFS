"""Historia 'Buen Fin' (1080x1920): 3X2 gigante + bloque BUEN FIN, cinco jerseys reales de la tienda en abanico.

Inspirada en el formato 'número grande | etiqueta roja + subtítulo' con fila de jerseys traslapadas.
Uso: python3 buen_fin.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import generar_ads as g
from generar_ads import put
from hf_ads import badge

OUT = g.HERE + "out/buenfin/"
W, H = 1080, 1920
INTER = "/usr/share/fonts/opentype/inter/"
RED, DARK_RED, INK = (186, 24, 30), (140, 14, 20), (20, 20, 22)
# back row first (drawn first), the centre one last so it sits in front
FAN = [
    ("cl_fcb_home26.png", -335, 0.72),
    ("cl_rm_away26.png", 335, 0.72),
    ("outfit/america.png", -205, 0.85),
    ("arg06.png", 205, 0.85),
    ("mex_gold.png", 0, 1.0),
]


def word(s, face, px, fill, track=-0.02):
    f = ImageFont.truetype(INTER + face, px)
    bb = f.getbbox(s)
    w = sum(f.getlength(c) for c in s) + track * px * (len(s) - 1)
    im = Image.new("RGBA", (int(w) + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 10
    for c in s:
        d.text((x, 10 - bb[1]), c, font=f, fill=fill)
        x += f.getlength(c) + track * px
    return im


def gradient_text(lay, top, bot):
    """Vertical red gradient inside the glyphs, like the reference's 5X3."""
    h = lay.height
    t = np.linspace(0, 1, h)[:, None, None]
    rgb = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    rgb = np.broadcast_to(rgb, (h, lay.width, 3)).astype(np.uint8)
    out = Image.fromarray(rgb).convert("RGBA")
    out.putalpha(lay.getchannel("A"))
    return out


def backdrop():
    yy = np.linspace(0, 1, H)[:, None]
    v = 252 - 10 * yy ** 2 + np.random.default_rng(1).normal(0, 0.7, (H, W))
    return Image.fromarray(np.dstack([v, v, v]).clip(0, 255).astype(np.uint8)).convert("RGBA")


def jersey(name, h):
    im = Image.open(g.SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    p = 60
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p + 12, p + 16))
    a = a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out


def headline(c, y):
    big = gradient_text(word("3X2", "InterDisplay-Black.otf", 250, (255, 255, 255), -0.04), (214, 40, 44), DARK_RED)
    tag = word("BUEN FIN", "InterDisplay-BlackItalic.otf", 74, (255, 255, 255), -0.02)
    box = Image.new("RGBA", (tag.width + 36, tag.height + 26), RED + (255,))
    box.alpha_composite(tag, (18, 13))
    l1 = word("LA MEJOR TEMPORADA", "Inter-SemiBold.otf", 30, INK, -0.01)
    l2 = word("DEL AÑO YA LLEGÓ", "Inter-SemiBold.otf", 30, INK, -0.01)
    gap = 34
    total = big.width + gap * 2 + 3 + box.width
    x = (W - total) // 2
    c.alpha_composite(big, (x, int(y - big.height / 2)))
    lx = x + big.width + gap
    ImageDraw.Draw(c).rectangle([lx, y - 125, lx + 2, y + 125], fill=RED)
    rx = lx + 3 + gap
    c.alpha_composite(box, (rx, int(y - 112)))
    c.alpha_composite(l1, (rx - 6, int(y + 8)))
    c.alpha_composite(l2, (rx - 6, int(y + 50)))


def build():
    c = backdrop()
    put(c, badge(140), W / 2, 230)
    headline(c, 520)
    for name, dx, k in FAN:
        lay = jersey(name, int(470 * k))
        put(c, lay, W / 2 + dx, 1060 + (1 - k) * 30)
    put(c, word("AGREGA 3 JERSEYS AL CARRITO. PAGA SOLO 2", "Inter-SemiBold.otf", 37, INK, -0.02), W / 2, 1470)
    pill = word("3 POR $1,600  ·  ENVÍO GRATIS", "InterDisplay-BlackItalic.otf", 44, (255, 255, 255), 0.0)
    box = Image.new("RGBA", (pill.width + 60, pill.height + 34), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([0, 0, box.width - 1, box.height - 1], radius=box.height // 2, fill=RED)
    box.alpha_composite(pill, (30, 17))
    put(c, box, W / 2, 1570)
    put(c, word("FOOTBALLFRENZY.SHOP  ·  PIDE POR DM", "Inter-SemiBold.otf", 28, (110, 110, 116), 0.06), W / 2, 1670)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "story-buen-fin.jpg", quality=94, subsampling=0)
    print("ok")
