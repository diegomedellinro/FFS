"""Historia 'Gracias por confiar en nosotros' con captura real de pedidos (nombres difuminados, fechas reales).
Uso: python3 historia_gracias.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put
from hf_ads import badge
from buenfin_logo import shadow
from buenfin_2da50 import bg, red, white, pill

OUT = g.HERE + "out/gracias/"
W, H = 1080, 1920
NAMES = [(60, 718, 700, 792), (60, 1252, 318, 1320), (60, 1722, 560, 1796)]   # customer names → blur


def captura(w=900, fechas=True):
    im = Image.open(g.SRC + "fotos/pedidos_semana.jpg").convert("RGB")
    for box in NAMES:
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box)
    if not fechas:                                   # drop the day headers, keep the orders
        segs = [(612, 1072), (1142, 1545), (1612, 1975)]
        parts = [im.crop((0, a, im.width, b)) for a, b in segs]
        out = Image.new("RGB", (im.width, sum(p.height for p in parts) + 40), (255, 255, 255))
        y = 20
        for p in parts:
            out.paste(p, (0, y))
            y += p.height
        im = out
    else:
        im = im.crop((0, 520, 1179, 1975))
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=36, fill=255)
    im.putalpha(m)
    return shadow(im, 0.6, 20)


def story(fechas=True):
    c = bg(W, H)
    put(c, badge(150), W / 2, 165)
    put(c, white("GRACIAS POR", 120, 0.01), W / 2, 330)
    put(c, red("CONFIAR EN NOSOTROS", 104, 0.01), W / 2, 460)
    put(c, captura(fechas=fechas), W / 2, 1100)
    put(c, white("Pedidos reales de esta semana" if fechas else "Nuestros últimos pedidos", 34, 0.06, "MontB.ttf"), W / 2, 1700)
    put(c, pill("¿EL TUYO CUÁNDO? · FOOTBALLFRENZY.SHOP", 42), W / 2, 1790)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    story().convert("RGB").save(OUT + "story-gracias.jpg", quality=94, subsampling=0)
    story(False).convert("RGB").save(OUT + "story-gracias-sin-fechas.jpg", quality=94, subsampling=0)
    print("ok")
