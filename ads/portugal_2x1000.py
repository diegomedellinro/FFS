"""Historias promo Portugal 2 x $1,000 (descuento automático en 6 modelos). 3 historias 1080x1920:
  1 hero con 2 jerseys y precio, 2 catálogo 'elige 2 de estos 6', 3 foto de Cristiano (src/fotos/cr7_portugal.jpg).
Uso: python3 portugal_2x1000.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from buenfin_logo import jersey, shadow
from buenfin_2da50 import bg, red, white, pill, burst, RED, GREY, WHITE

OUT = g.HERE + "out/portugal_2x1000/"
W, H = 1080, 1920
GREEN = (0, 120, 60)
P = g.SRC + "portugal/"
MODELS = [  # (image, name) — the 6 products in the automatic discount
    ("pt2004_cr7.png", "RETRO 2004 · CR7"), ("pt2026_home7.png", "LOCAL 2026"), ("pt2026_away.png", "VISITA 2026"),
    ("pt_eusebio26.png", "EUSÉBIO 2026"), ("pt_eusebio25.png", "EUSÉBIO 2025"), ("pt_eusebio25_ls.png", "EUSÉBIO 2025 M/L"),
]


def flag_bar(c, y, w=360, h=10):
    d = ImageDraw.Draw(c)
    x0 = (W - w) / 2
    d.rectangle([x0, y, x0 + w * 0.4, y + h], fill=GREEN)
    d.rectangle([x0 + w * 0.4, y, x0 + w, y + h], fill=RED)


def price_block(c, y):
    put(c, text("ANTES $1,600", "Anton.ttf", 64, GREY, 0.02, strike=RED), W / 2, y)
    put(c, white("2 POR $1,000", 170, 0.01), W / 2, y + 150)


def hero():
    c = bg(W, H)
    put(c, badge(160), W / 2, 180)
    put(c, white("PROMO PORTUGAL", 70, 0.08, "MontB.ttf"), W / 2, 330)
    flag_bar(c, 380)
    put(c, red("2 x $1,000", 230, 0.01), W / 2, 530)
    put(c, white("EN JERSEYS DE PORTUGAL", 70, 0.02), W / 2, 690)
    put(c, jersey("portugal/pt2004_cr7.png", 430, -7), W / 2 - 215, 1060)
    put(c, jersey("portugal/pt2026_home7.png", 430, 7), W / 2 + 215, 1080)
    put(c, burst(110, "-$600"), W / 2 + 380, 850)
    price_block(c, 1370)
    put(c, pill("AUTOMÁTICO EN EL CARRITO · SIN CÓDIGO", 40), W / 2, 1690)
    put(c, white("FOOTBALLFRENZY.SHOP · ENVÍO GRATIS · PIDE POR DM", 28, 0.08, "MontB.ttf"), W / 2, 1810)
    return c


def tile(img, name, w=440, h=430):
    t = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(t).rounded_rectangle([0, 0, w - 1, h - 1], radius=26, fill=(250, 250, 250, 255))
    im = Image.open(P + img).convert("RGBA")
    if img.endswith(".jpg"):                       # product photo on white: trim the margin
        m = round(im.width * 0.06)
        im = im.crop((m, m, im.width - m, im.height - m))
    else:
        im = im.crop(im.getchannel("A").getbbox())
    im.thumbnail((w - 70, h - 120), Image.LANCZOS)
    t.alpha_composite(im, ((w - im.width) // 2, 24 + (h - 120 - im.height) // 2 + 10))
    lab = text(name, "Anton.ttf", 38, (20, 20, 20), 0.02)
    t.alpha_composite(lab, ((w - lab.width) // 2, h - 70))
    return shadow(t, 0.55, 14)


def catalogo():
    c = bg(W, H)
    put(c, badge(130), W / 2, 150)
    put(c, white("ELIGE 2 DE ESTOS", 96, 0.01), W / 2, 300)
    put(c, red("6 MODELOS", 150, 0.01), W / 2, 435)
    flag_bar(c, 525)
    for i, (img, name) in enumerate(MODELS):
        x = W / 2 + (-1 if i % 2 == 0 else 1) * 240
        y = 790 + (i // 2) * 360
        put(c, tile(img, name, 440, 340), x, y)
    put(c, pill("2 POR $1,000 · AUTOMÁTICO EN EL CARRITO", 44), W / 2, 1745)
    put(c, white("FOOTBALLFRENZY.SHOP · PIDE POR DM", 28, 0.08, "MontB.ttf"), W / 2, 1830)
    return c


def foto_cr7():
    ph = Image.open(g.SRC + "fotos/cr7_portugal.jpg").convert("RGB")
    s = W / ph.width
    ph = ph.resize((W, round(ph.height * s)), Image.LANCZOS).crop((0, 0, W, H))
    ph = ImageEnhance.Brightness(ph).enhance(0.8).convert("RGBA")
    # darken bottom for text
    grad = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(max(0, v - 90) * 1.6))
    ph.alpha_composite(Image.composite(Image.new("RGBA", (W, H), (8, 8, 10, 255)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), grad))
    c = ph
    put(c, badge(140), 110, 120)
    put(c, white("EL BICHO", 150, 0.01), W / 2, 1180)
    put(c, white("EN DOBLETE", 150, 0.01), W / 2, 1330)
    put(c, red("2 JERSEYS DE PORTUGAL POR $1,000", 66, 0.01), W / 2, 1470)
    put(c, text("ANTES $1,600", "Anton.ttf", 54, GREY, 0.02, strike=RED), W / 2, 1570)
    put(c, pill("AUTOMÁTICO EN EL CARRITO · SIN CÓDIGO", 40), W / 2, 1680)
    put(c, white("FOOTBALLFRENZY.SHOP · ENVÍO GRATIS · PIDE POR DM", 28, 0.08, "MontB.ttf"), W / 2, 1810)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n, fn in (("1-portugal-2x1000", hero), ("2-portugal-elige-2", catalogo), ("3-portugal-bicho", foto_cr7)):
        fn().convert("RGB").save(OUT + n + ".jpg", quality=94, subsampling=0)
    print("ok")
