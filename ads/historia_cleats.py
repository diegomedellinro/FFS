"""Historia 'Nuevos cleats ya llegaron' (1080x1920) con los 5 tacos más nuevos de la tienda (fotos de producto en tarjetas).
Uso: python3 historia_cleats.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from buenfin_logo import shadow
from buenfin_2da50 import bg, red, white, pill

OUT = g.HERE + "out/cleats/"
W, H = 1080, 1920
HERO = ("predator.jpg", "ADIDAS PREDATOR ELITE TONGUE")
REST = [("f50y.jpg", "F50 HYPERFAST ELITE"), ("phantom.jpg", "NIKE PHANTOM 6 ELITE"),
        ("beckham.jpg", "PREDATOR x BECKHAM"), ("f50m.jpg", "F50 HYPERFAST PRO")]


def card(img, name, w, h, label_px):
    im = Image.open(g.SRC + "cleats/" + img).convert("RGB")
    paper = im.getpixel((4, 4))
    t = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(t).rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=paper + (255,))
    m = round(im.width * 0.04)
    im = im.crop((m, m, im.width - m, im.height - m))
    lab_h = label_px + 34
    im.thumbnail((w - 30, h - lab_h - 10), Image.LANCZOS)
    t.paste(im, ((w - im.width) // 2, (h - lab_h - im.height) // 2 + 6))
    lab = text(name, "Anton.ttf", label_px, (18, 18, 18), 0.02)
    t.alpha_composite(lab, ((w - lab.width) // 2, h - lab_h + 4))
    return shadow(t, 0.55, 16)


def story():
    c = bg(W, H)
    put(c, badge(130), W / 2, 140)
    put(c, white("NUEVOS CLEATS", 150, 0.01), W / 2, 300)
    put(c, red("YA LLEGARON", 120, 0.01), W / 2, 435)
    put(c, card(*HERO, 920, 520, 44), W / 2, 790)
    for i, (img, name) in enumerate(REST):
        x = W / 2 + (-1 if i % 2 == 0 else 1) * 235
        y = 1245 + (i // 2) * 280
        put(c, card(img, name, 450, 260, 30), x, y)
    put(c, pill("$1,800 · ENVÍO GRATIS A TODO MÉXICO", 44), W / 2, 1737)
    put(c, white("FOOTBALLFRENZY.SHOP · PIDE POR DM", 28, 0.08, "MontB.ttf"), W / 2, 1828)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    story().convert("RGB").save(OUT + "story-nuevos-cleats.jpg", quality=94, subsampling=0)
    print("ok")
