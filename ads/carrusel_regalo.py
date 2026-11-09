"""Carrusel meme '🗣️ No sé qué regalarte / Yo:' (8 slides, 1080x1350), fondo blanco y Anton negro como el original.

1: portada con el meme (la persona que 'presenta' viene de la captura del usuario; solo para orgánico).
2-7: cada jersey 'presentada' con un remate corto. 8: cierre con oferta + CTA.
Uso: python3 carrusel_regalo.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from chat_doctor import emoji

OUT = g.HERE + "out/regalo/"
W, H = 1080, 1350
INK, RED, GREY = (12, 12, 12), (225, 30, 45), (110, 110, 116)
PERSON = g.HERE + "src/fotos/meme_regalo_persona.png"

SLIDES = [
    ("viejo/rm1213.png", "Para el que dice", "\"ya tengo muchas\""),
    ("spotify/golf.png", "Para el culé", "que vive en TikTok"),
    ("src_portugal", "Para el fan del 🐐", "de toda la vida"),
    ("viejo/ame1213.png", "Para el americanista", "que no supera el 2013"),
    ("kaka.png", "Para el que dice", "\"el fútbol de antes era mejor\""),
    ("mex_gold.png", "Para el que solo", "se pone la de México en el Mundial"),
]


def line(c, s, y, px=96, fill=INK):
    """Anton line; supports one emoji at the end (rendered with Noto)."""
    if "🐐" in s or "🗣️" in s:
        e = "🐐" if "🐐" in s else "🗣️"
        t = s.replace(e, "").strip()
        lay = text(t, "Anton.ttf", px, fill, 0.0)
        em = emoji(e, int(px * 0.95))
        w = lay.width + 12 + em.width
        x = (W - w) // 2
        if s.startswith(e):
            c.alpha_composite(em, (x, int(y - em.height / 2)))
            c.alpha_composite(lay, (x + em.width + 12, int(y - lay.height / 2)))
        else:
            c.alpha_composite(lay, (x, int(y - lay.height / 2)))
            c.alpha_composite(em, (x + lay.width + 12, int(y - em.height / 2)))
        return
    lay = text(s, "Anton.ttf", px, fill, 0.0)
    if lay.width > W - 100:
        lay = lay.resize((W - 100, round(lay.height * (W - 100) / lay.width)), Image.LANCZOS)
    put(c, lay, W / 2, y)


def jersey(name, maxw=760, maxh=760):
    path = g.SRC + ("portugal/pt2004_cr7.png" if name == "src_portugal" else name)
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    s = min(maxw / im.width, maxh / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    p = 60
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p + 10, p + 22))
    a = a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.30))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out


def blank():
    return Image.new("RGBA", (W, H), (255, 255, 255, 255))


def footer(c, n):
    put(c, badge(84), 80, H - 70)
    put(c, text(f"{n}/8", "MontB.ttf", 26, GREY, 0.05), W - 70, H - 70)


def cover():
    c = blank()
    line(c, "🗣️ “No sé qué regalarte”", 150, 92)
    line(c, "Yo:", 330, 110)
    if os.path.exists(PERSON):
        p = Image.open(PERSON).convert("RGBA")
        p = p.crop(p.getchannel("A").getbbox())
        s = 840 / p.height
        p = p.resize((round(p.width * s), 840), Image.LANCZOS)
        c.alpha_composite(p, ((W - p.width) // 2 + 40, H - p.height - 30))
    footer(c, 1)
    return c


def slide(n, name, top, bottom):
    c = blank()
    line(c, top, 130, 84)
    line(c, bottom, 235, 84, RED)
    put(c, jersey(name), W / 2, 770)
    footer(c, n)
    return c


def cierre():
    c = blank()
    line(c, "Ya no hay excusa", 330, 110)
    line(c, "para no saber qué regalar 🎁".replace(" 🎁", ""), 450, 76)
    put(c, emoji("🎁", 150), W / 2, 640)
    line(c, "3 POR $1,600", 830, 120, RED)
    put(c, text("3X2 AUTOMÁTICO  ·  ENVÍO GRATIS A TODO MÉXICO", "MontB.ttf", 32, INK, 0.06), W / 2, 940)
    put(c, text("PIDE POR DM O EN FOOTBALLFRENZY.SHOP", "MontB.ttf", 32, GREY, 0.06), W / 2, 1000)
    put(c, badge(150), W / 2, 1170)
    put(c, text("8/8", "MontB.ttf", 26, GREY, 0.05), W - 70, H - 70)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [cover()] + [slide(i + 2, *s) for i, s in enumerate(SLIDES)] + [cierre()]
    for i, s in enumerate(slides, 1):
        s.convert("RGB").save(f"{OUT}{i:02d}.jpg", quality=93, subsampling=0)
    print(len(slides), "slides")
