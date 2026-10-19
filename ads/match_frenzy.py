"""Carrusel "MATCH FRENZY": jerseys de pareja (mismo equipo o rivales) con sugerencia de outfit.

Inspirado en el formato de carruseles de outfits de pareja, usando solo fotos de producto
de la tienda (sin imágenes de terceros).
Formato 1080x1350 (4:5). Uso: python3 match_frenzy.py
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import text, rich, pill, put, WHITE, RED, INK, GREY

W, H = 1080, 1350
OUT = g.HERE + "out/match/"
BG = (246, 245, 242)
DARK = (17, 17, 19)


# ---------------------------------------------------------------- slides

def label(c, cx, y, who, team):
    put(c, text(who, "MontB.ttf", 26, RED, 0.18), cx, y)
    put(c, text(team, "Inter-Bold.otf", 32, DARK), cx, y + 44)


def footer_brand(c):
    b = g.brand(24)
    arr = np.array(b)
    mask = (arr[..., 0] > 200) & (arr[..., 1] > 200)
    arr[mask, 0:3] = DARK
    put(c, Image.fromarray(arr), W / 2, H - 50)


def make_slide(pair, title, sub, names, tip, num):
    c = Image.new("RGBA", (W, H), BG + (255,))
    # soft colour halo behind each jersey
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(halo)
    d.ellipse([60, 330, 560, 830], fill=(255, 26, 43, 26))
    d.ellipse([520, 330, 1020, 830], fill=(17, 17, 19, 22))
    c.alpha_composite(halo.filter(ImageFilter.GaussianBlur(60)))
    put(c, text(f"{num:02d}", "Anton.ttf", 34, RED, 0.05), W / 2, 62)
    put(c, text(title, "Anton.ttf", 104, DARK, 0.01), W / 2, 140)
    put(c, text(sub, "Inter-SemiBold.otf", 32, (95, 95, 100)), W / 2, 228)
    g.product(c, pair[0], W * 0.27, 590, 460, 540, 1, 1, -5)
    g.product(c, pair[1], W * 0.73, 610, 460, 540, 1, 1, 5)
    # little heart between them
    put(c, text("+", "Anton.ttf", 90, RED), W / 2, 600)
    label(c, W * 0.27, 905, "TÚ", names[0])
    label(c, W * 0.73, 905, "TU OTRA MITAD", names[1])
    # outfit tip
    box = Image.new("RGBA", (920, 120), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([0, 0, 919, 119], radius=26, fill=(255, 255, 255, 255), outline=(225, 223, 218, 255), width=2)
    put(c, box, W / 2, 1075)
    put(c, text("COMBÍNALAS CON", "MontB.ttf", 22, (120, 120, 126), 0.16), W / 2, 1050)
    put(c, text(tip, "Inter-Bold.otf", 32, DARK), W / 2, 1093)
    put(c, rich((("2 jerseys $1,600", DARK), ("  ·  ", (150, 150, 150)), ("la 3ra GRATIS con el 3x2", RED)), "Inter-Bold.otf", 32), W / 2, 1200)
    footer_brand(c)
    return c


SLIDES = [
    ("01-portada-real-madrid", ("rm125.png", "rm_away.png"), "MATCH FRENZY", "Real Madrid · blanco y verde", ("125 aniversario", "Visitante 26/27"), "jeans claros + tenis blancos", 1),
    ("02-barca", ("barca_away.png", "barca3.png"), "MATCH FRENZY", "Barça · noche y turquesa", ("Visitante 26/27", "Tercera 26/27"), "jeans oscuros + tenis negros", 2),
    ("03-clasico-mx", ("america110.png", "chivas3.png"), "AMOR DE CLÁSICO", "América y Chivas en la misma casa", ("América 110 años", "Chivas tercera 26/27"), "jeans anchos + tenis de suela café", 3),
    ("04-argentina", ("arg_last.png", "arg06.png"), "MATCH FRENZY", "Argentina · Last Dance y retro 2006", ("Last Dance 2026", "Retro 2006"), "jeans claros + tenis blancos", 4),
    ("05-retro", ("mu0708.png", "kaka.png"), "MATCH RETRO", "United 07/08 y Milan 06/07", ("United 07/08 manga larga", "Milan 06/07"), "jeans oscuros + tenis retro", 5),
]


def cierre():
    c = Image.new("RGBA", (W, H), DARK + (255,))
    c.alpha_composite(g.background(W, H, ((0.5, 0.55, 0.6, RED, 0.5),)).copy())
    put(c, g.brand(26), W / 2, 90)
    put(c, text("¿HACEMOS", "Anton.ttf", 150, WHITE, 0.01), W / 2, 290)
    put(c, rich((("MATCH", RED), ("?", WHITE)), "Anton.ttf", 150), W / 2, 450)
    put(c, text("Etiqueta a tu otra mitad", "Inter-Bold.otf", 46, WHITE), W / 2, 590)
    for i, (name, dx, rot) in enumerate([("rm125.png", -0.2, -8), ("barca_away.png", 0.2, 8)]):
        g.product(c, name, W / 2 + dx * W, 840, 380, 330, 1, 1, rot)
    put(c, rich((("2 jerseys = ", WHITE), ("la 3ra GRATIS", RED)), "Anton.ttf", 70), W / 2, 1080)
    put(c, text("3x2 en todas las jerseys · Tallas S a 4XL · Envío gratis", "Inter-SemiBold.otf", 30, GREY), W / 2, 1150)
    put(c, g.cta("ARMEN SU MATCH EN FOOTBALLFRENZY.SHOP", 900, 34), W / 2, 1250)
    return c


if __name__ == "__main__":
    import sys
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    for name, pair, title, sub, names, tip, num in SLIDES:
        if only and name not in only:
            continue
        make_slide(pair, title, sub, names, tip, num).convert("RGB").save(f"{OUT}{name}.jpg", quality=93, subsampling=0)
        print(name)
    if not only or "06-cierre" in only:
        cierre().convert("RGB").save(f"{OUT}06-cierre.jpg", quality=93, subsampling=0)
        print("06-cierre")
