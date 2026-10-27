"""Ad 'FC Barcelona x Golf' estilo editorial (inspo: Real Zaragoza 'Detalles · Home Kit').

Foto: out/hf_ads/raw/barca-outpaint.png (foto del cliente ampliada hacia arriba con Higgsfield outpaint).
Salidas: out/hf_ads/barca-golf-historia.jpg (1080x1920) y barca-golf-feed.jpg (1080x1350).
Uso: python3 barca_golf.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import generar_ads as g
from generar_ads import text, put
from hf_ads import badge, gradient

SRC = g.HERE + "out/hf_ads/raw/barca-outpaint.png"
OUT = g.HERE + "out/hf_ads/"
SERIF = g.HERE + "fonts/PlayfairDisplay-SemiBold.ttf"
ITAL = g.HERE + "fonts/PlayfairDisplay-MediumItalic.ttf"
WHITE = (255, 255, 255)


def serif(s, px, path=SERIF, track=0.0, fill=WHITE):
    f = ImageFont.truetype(path, int(px))
    bb = f.getbbox(s)
    tw = sum(f.getlength(c) for c in s) + track * px * (len(s) - 1)
    pad = int(px * 0.2)
    im = Image.new("RGBA", (int(tw) + 2 * pad, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad
    for c in s:
        d.text((x, pad - bb[1]), c, font=f, fill=fill)
        x += f.getlength(c) + track * px
    return im


def caps(s, px, track=0.28, fill=WHITE):
    return text(s, "MontB.ttf", int(px), fill, track)


def lockup(h):
    """'FOOTBALLFRENZY.SHOP | logo' like the adidas | crest corner."""
    t = caps("FOOTBALLFRENZY.SHOP", h * 0.26, 0.16)
    b = badge(int(h))
    w = t.width + 30 + 4 + 18 + b.width
    im = Image.new("RGBA", (w, b.height), (0, 0, 0, 0))
    im.alpha_composite(t, (0, (b.height - t.height) // 2))
    ImageDraw.Draw(im).line([(t.width + 30, b.height * .3), (t.width + 30, b.height * .7)], fill=WHITE + (200,), width=3)
    im.alpha_composite(b, (t.width + 52, 0))
    return im


def base(W, H, top_crop):
    im = Image.open(SRC).convert("RGB")
    s = W / im.width
    im = im.resize((W, round(im.height * s)), Image.LANCZOS)
    y0 = int(top_crop * im.height)
    return im.crop((0, y0, W, y0 + H)).convert("RGBA")


def compose(W, H, top_y, cta_y, top_crop=0.0):
    c = base(W, H, top_crop)
    gradient(c, top=True, h=0.36, k=0.62)
    gradient(c, top=False, h=0.34, k=0.88)
    put(c, caps("3X2 ACTIVO", 30, 0.45), W / 2, top_y)
    put(c, serif("FC BARCELONA", 118, track=0.01), W / 2, top_y + 105)
    put(c, serif("x Golf", 74, ITAL), W / 2, top_y + 210)
    put(c, serif("Haz tu pedido por mensaje directo", 44, ITAL), W / 2, cta_y)
    put(c, serif("o en el sitio web", 44, ITAL), W / 2, cta_y + 58)
    put(c, lockup(90), W / 2, cta_y + 150)
    return c


if __name__ == "__main__":
    compose(1080, 1920, 230, 1580).convert("RGB").save(OUT + "barca-golf-historia.jpg", quality=94, subsampling=0)
    compose(1080, 1350, 80, 1110, top_crop=0.04).convert("RGB").save(OUT + "barca-golf-feed.jpg", quality=94, subsampling=0)
    print("ok")
