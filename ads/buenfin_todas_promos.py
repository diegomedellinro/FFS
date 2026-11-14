"""Historia 'Todas nuestras promos del Buen Fin' (1080x1920): 3x2, 5x3, 2da al 50% (BUENFIN), Portugal 2 x $1,000, envío gratis.
Uso: python3 buenfin_todas_promos.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from buenfin_2da50 import bg, red, white, pill, RED, GREY, WHITE

OUT = g.HERE + "out/buenfin_promos/"
W, H = 1080, 1920
PROMOS = [
    ("3x2", "3 JERSEYS POR $1,600", "AUTOMÁTICO EN EL CARRITO", "encargo/atlante.png"),
    ("5x3", "5 JERSEYS POR $2,400", "AUTOMÁTICO EN EL CARRITO", "america110.png"),
    ("-50%", "LA 2DA JERSEY AL 50%", "CON EL CÓDIGO BUENFIN", "psg_home26.png"),
    ("2x$1,000", "2 JERSEYS DE PORTUGAL", "EDICIÓN CRISTIANO · AUTOMÁTICO", "portugal/pt2004_cr7.png"),
]


def card(big, title, sub, jname, w=960, h=210):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=28, fill=(18, 18, 21, 240), outline=(70, 20, 24, 255), width=2)
    d.rounded_rectangle([0, 0, 14, h - 1], radius=7, fill=RED + (255,))
    px = 124
    b = text(big, "Anton.ttf", px, RED, 0.0)
    while b.width > 228:
        px -= 4
        b = text(big, "Anton.ttf", px, RED, 0.0)
    c.alpha_composite(b, (44 + (230 - b.width) // 2, (h - b.height) // 2))
    d.line([(300, 40), (300, h - 40)], fill=(60, 60, 66, 255), width=2)
    t = text(title, "Anton.ttf", 52, WHITE, 0.01)
    s = text(sub, "MontB.ttf", 22, GREY, 0.08)
    c.alpha_composite(t, (330, h // 2 - t.height + 4))
    c.alpha_composite(s, (332, h // 2 + 18))
    return c


def story():
    c = bg(W, H)
    put(c, badge(170), W / 2, 190)
    put(c, pill("BUEN FIN · 13 AL 17 DE NOVIEMBRE", 40), W / 2, 345)
    put(c, white("TODAS NUESTRAS", 104, 0.01), W / 2, 465)
    put(c, red("PROMOS", 230, 0.01), W / 2, 625)
    for i, p in enumerate(PROMOS):
        put(c, card(*p), W / 2, 870 + i * 232)
    put(c, pill("+ ENVÍO GRATIS A TODO MÉXICO 🇲🇽".replace(" 🇲🇽", ""), 50), W / 2, 1650 + 95)
    put(c, white("FOOTBALLFRENZY.SHOP · PIDE POR DM", 30, 0.08, "MontB.ttf"), W / 2, 1832)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    story().convert("RGB").save(OUT + "story-todas-las-promos.jpg", quality=94, subsampling=0)
    print("ok")
