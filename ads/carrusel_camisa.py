"""Carrusel 'Lo que tu jersey dice de ti · parte 1' (10 slides, 1080x1350).

Fondo hueso, logo arriba, título negro con 'parte 1' en itálica, jersey real de la tienda al centro
con sombra suave y un remate corto abajo. Slide 10: pregunta + oferta + CTA.
Uso: python3 carrusel_camisa.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge

OUT = g.HERE + "out/camisa/"
W, H = 1080, 1350
BG, INK, GREY, RED = (224, 222, 208), (24, 24, 24), (95, 95, 92), (205, 30, 42)
INTER = "/usr/share/fonts/opentype/inter/"
TITLE = g.HERE + "fonts/MontB.ttf"

SLIDES = [
    ("barca_away.png", "La pediste desde el día que salió y ya la presumiste en todas tus historias."),
    ("rm1718.png", "Todavía ves los goles de CR7 en YouTube antes de dormir."),
    ("viejo/ame1213.png", "Sigues gritando el cabezazo de Moisés Muñoz en la final del 2013."),
    ("spotify/golf.png", "Te sabes más canciones de Tyler que jugadores del Barça."),
    ("kaka.png", "Para ti el fútbol bonito se acabó cuando Kaká dejó el Milan."),
    ("mex_gold.png", "Eres aficionado del Tri cada cuatro años… y no te da pena."),
    ("zidane98.png", "Tu papá te contó tantas veces lo del 98 que sientes que lo viste."),
    ("portugal/pt2004_cr7.png", "Antes que de cualquier club, eres de Cristiano."),
    ("viejo/fcb0809.png", "Para ti el sextete fue ayer y nadie te va a convencer de lo contrario."),
]


def font(name, px):
    return ImageFont.truetype(name if name.startswith("/") else INTER + name, px)


def title(c, y=300):
    f = ImageFont.truetype(TITLE, 82)
    fi = font("InterDisplay-SemiBoldItalic.otf", 76)
    d = ImageDraw.Draw(c)
    l1 = "LO QUE TU JERSEY"
    d.text((W / 2, y), l1, font=f, fill=INK, anchor="mm")
    l2a, l2b = "DICE DE TI ", "parte 1"
    wa, wb = d.textlength(l2a, font=f), d.textlength(l2b, font=fi)
    x = (W - wa - wb) / 2
    d.text((x, y + 92), l2a, font=f, fill=INK, anchor="lm")
    d.text((x + wa, y + 96), l2b, font=fi, fill=INK, anchor="lm")


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def caption(c, s, y=1150):
    d = ImageDraw.Draw(c)
    f = font("Inter-SemiBold.otf", 44)
    for i, line in enumerate(wrap(d, s, f, 800)):
        d.text((W / 2, y + i * 58), line, font=f, fill=INK, anchor="mm")


def jersey(name, maxw=640, maxh=560):
    im = Image.open(g.SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    s = min(maxw / im.width, maxh / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    p = 60
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p + 6, p + 20))
    a = a.filter(ImageFilter.GaussianBlur(20)).point(lambda v: int(v * 0.32))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (40, 38, 30, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out


def base(n):
    c = Image.new("RGBA", (W, H), BG + (255,))
    put(c, badge(130), W / 2, 130)
    d = ImageDraw.Draw(c)
    d.text((W - 60, H - 50), f"{n}/10", font=font("Inter-SemiBold.otf", 26), fill=GREY, anchor="rm")
    return c


def slide(n, name, line):
    c = base(n)
    title(c)
    put(c, jersey(name), W / 2, 760)
    caption(c, line)
    return c


def cierre():
    c = base(10)
    d = ImageDraw.Draw(c)
    f = ImageFont.truetype(TITLE, 92)
    for i, s in enumerate(["¿CUÁL DICE", "MÁS DE TI?"]):
        d.text((W / 2, 400 + i * 108), s, font=f, fill=INK, anchor="mm")
    d.text((W / 2, 640), "Comenta el número 👇".replace(" 👇", ""), font=font("InterDisplay-SemiBoldItalic.otf", 56), fill=GREY, anchor="mm")
    put(c, text("3 POR $1,600 · 5 POR $2,400", "Anton.ttf", 84, RED, 0.02), W / 2, 820)
    d.text((W / 2, 930), "3x2 y 5x3 automáticos · envío gratis a todo México", font=font("Inter-SemiBold.otf", 36), fill=INK, anchor="mm")
    d.text((W / 2, 990), "Pide por DM o en footballfrenzy.shop", font=font("Inter-SemiBold.otf", 36), fill=GREY, anchor="mm")
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [slide(i + 1, *s) for i, s in enumerate(SLIDES)] + [cierre()]
    for i, s in enumerate(slides, 1):
        s.convert("RGB").save(f"{OUT}{i:02d}.jpg", quality=93, subsampling=0)
    print(len(slides), "slides")
