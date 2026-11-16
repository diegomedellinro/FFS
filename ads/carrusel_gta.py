"""Carrusel 'Tu jersey cuando salió el GTA V vs. cuando sale el GTA VI' (1080x1350, 5 slides).
Cuadrícula 2x2 como la referencia, pero con estilo de marca y sin logos del juego: los años y el número romano son tipografía propia.
Uso: python3 carrusel_gta.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text, background
from hf_ads import badge
from buenfin_logo import jersey, shadow
from buenfin_2da50 import red, white, pill, RED, GREY, WHITE

OUT = g.HERE + "out/carrusel_gta/"
W, H = 1080, 1350
PAIRS = [  # (club, antes, ahora)
    ("REAL MADRID", "cl_rm_1314.png", "cl_rm_third26.png"),
    ("FC BARCELONA", "fcb_1415_home.png", "cl_fcb_home26.png"),
    ("CLUB AMÉRICA", "viejo/ame1213.png", "america110.png"),
    ("REAL MADRID VISITA", "cl_rm_1213away.png", "cl_rm_away26.png"),
]
TOP, GAP = 150, 10                       # header band height, divider width
CW, CH = (W - GAP) // 2, (H - TOP - 90 - GAP) // 2


def base(n):
    c = background(W, H, glows=((0.5, 0.55, 0.8, (120, 8, 14), 0.6),)).copy()
    put(c, badge(84), 70, 75)
    put(c, text(f"{n}/5", "MontB.ttf", 26, GREY, 0.05), W - 70, 75)
    return c


LOGOS = Image.open(g.SRC + "fotos/gta_logos.jpg").convert("RGB")      # logos del usuario (contenido orgánico)
LOGO_BOX = {"V": (0, 60, 545, 620), "VI": (0, 790, 545, 1350)}


def era_tile(year, roman, caption):
    """Tile with the user's game logo art and a small year pill."""
    im = LOGOS.crop(LOGO_BOX[roman])
    s = max(CW / im.width, CH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = (im.width - CW) // 2, (im.height - CH) // 2
    t = im.crop((x0, y0, x0 + CW, y0 + CH)).convert("RGBA")
    yp = pill(year, 40)
    t.alpha_composite(yp, ((CW - yp.width) // 2, CH - yp.height - 24))
    return t


def era_tile_text(year, roman, caption):
    t = Image.new("RGBA", (CW, CH), (14, 14, 16, 255))
    r = text(roman, "Anton.ttf", 230, RED, 0.0)
    y = text(year, "Anton.ttf", 84, WHITE, 0.04)
    cap = text(caption, "MontB.ttf", 22, GREY, 0.1)
    total = r.height + 18 + y.height + 26 + cap.height
    top = (CH - total) // 2
    t.alpha_composite(r, ((CW - r.width) // 2, top))
    t.alpha_composite(y, ((CW - y.width) // 2, top + r.height + 18))
    t.alpha_composite(cap, ((CW - cap.width) // 2, top + r.height + 18 + y.height + 26))
    return t


def jersey_tile(name):
    t = Image.new("RGBA", (CW, CH), (236, 236, 232, 255))
    j = jersey(name, int(CH * 0.8), 0, dark=False)
    j.thumbnail((CW - 30, CH - 20), Image.LANCZOS)
    t.alpha_composite(j, ((CW - j.width) // 2, (CH - j.height) // 2))
    return t


def grid(c, antes, ahora):
    y0 = TOP
    c.alpha_composite(era_tile("2013", "V", "CUANDO SALIÓ EL GTA V"), (0, y0))
    c.alpha_composite(jersey_tile(antes), (CW + GAP, y0))
    c.alpha_composite(era_tile("2026", "VI", "CUANDO SALE EL GTA VI"), (0, y0 + CH + GAP))
    c.alpha_composite(jersey_tile(ahora), (CW + GAP, y0 + CH + GAP))
    d = ImageDraw.Draw(c)
    d.rectangle([CW, y0, CW + GAP - 1, y0 + 2 * CH + GAP], fill=RED)
    d.rectangle([0, y0 + CH, W, y0 + CH + GAP - 1], fill=RED)


def slide(n, club, antes, ahora):
    c = base(n)
    put(c, white(club, 64, 0.03), W / 2, 75)
    grid(c, antes, ahora)
    put(c, text("¿CUÁL TE QUEDAS? COMENTA V O VI", "MontB.ttf", 26, WHITE, 0.08), W / 2, H - 45)
    return c


def cierre():
    c = base(5)
    put(c, white("EL GTA VI", 140, 0.01), W / 2, 330)
    put(c, red("TARDÓ 13 AÑOS", 130, 0.01), W / 2, 480)
    put(c, white("TU JERSEY NUEVA LLEGA EN DÍAS", 60, 0.02), W / 2, 640)
    put(c, pill("3 POR $1,600 · 5 POR $2,400", 56), W / 2, 820)
    put(c, text("3x2 y 5x3 automáticos · envío gratis a todo México", "MontB.ttf", 28, WHITE, 0.03), W / 2, 930)
    put(c, text("Pide por DM o en footballfrenzy.shop", "MontB.ttf", 28, GREY, 0.03), W / 2, 985)
    put(c, badge(170), W / 2, 1170)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [slide(i + 1, *p) for i, p in enumerate(PAIRS)] + [cierre()]
    for i, s in enumerate(slides, 1):
        s.convert("RGB").save(f"{OUT}{i:02d}.jpg", quality=93, subsampling=0)
    print(len(slides))
