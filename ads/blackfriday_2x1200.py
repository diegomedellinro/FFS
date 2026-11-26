"""Anuncios Black Friday '2 jerseys por $1,200 · la 2da al 50%' (FB/IG): 3 diseños x 2 formatos (1080x1350 y 1080x1920).
A: El Clásico (Barça + Madrid), B: doble Madrid, C: doble Barça. Estilo de marca negro/rojo.
Uso: python3 blackfriday_2x1200.py
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text, background
from hf_ads import badge
from buenfin_logo import jersey, shadow
from buenfin_2da50 import red, white, pill, burst, RED, GREY, WHITE

OUT = g.HERE + "out/blackfriday/"
URL = "FOOTBALLFRENZYSHOP.STORE"
DESIGNS = {
    "clasico": ("EL CLÁSICO DEL BLACK FRIDAY", ("cl_fcb_home26.png", (40, 60, 160)), ("rm_home26_v2.png", (210, 210, 220))),
    "madrid": ("DOBLE MADRIDISTA", ("rm_home26_v2.png", (210, 210, 220)), ("cl_rm_third26.png", (200, 40, 90))),
    "barca": ("DOBLE CULÉ", ("cl_fcb_home26.png", (40, 60, 160)), ("cl_fcb_third26.png", (60, 200, 180))),
}


def outline_text(s, px, col=(255, 255, 255), a=40, width=3):
    t = text(s, "Anton.ttf", px, col, 0.0)
    m = t.getchannel("A")
    edge = m.filter(ImageFilter.MaxFilter(width * 2 + 1)).point(lambda v: 255 if v > 128 else 0)
    inner = m.point(lambda v: 255 if v > 128 else 0)
    ring = Image.fromarray(np.clip(np.asarray(edge, int) - np.asarray(inner, int), 0, 255).astype(np.uint8))
    out = Image.new("RGBA", t.size, col + (0,))
    out.putalpha(ring.point(lambda v: v * a // 255))
    return out


def base(W, H, c1, c2):
    c = background(W, H, glows=((0.22, 0.58, 0.55, c1, 0.45), (0.78, 0.58, 0.55, c2, 0.30),
                                (0.5, 0.05, 0.6, (150, 10, 18), 0.35))).copy()
    # giant faint BLACK FRIDAY watermark
    for i, s in enumerate(("BLACK", "FRIDAY")):
        wm = outline_text(s, int(W * 0.34), a=55)
        put(c, wm, W / 2, H * (0.40 + 0.2 * i))
    d = ImageDraw.Draw(c)
    for y in (48, H - 48):
        d.line([(60, y), (W - 60, y)], fill=RED, width=3)
    return c


def tag(price, old=None):
    t = text(price, "Anton.ttf", 64, WHITE, 0.0)
    o = text(old, "Anton.ttf", 34, (255, 210, 210), 0.0, strike=WHITE) if old else None
    w = t.width + 60 + ((o.width + 20) if o else 0)
    b = Image.new("RGBA", (w, t.height + 28), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, w - 1, b.height - 1], radius=b.height // 2, fill=RED + (255,), outline=WHITE + (255,), width=3)
    x = 30
    if o:
        b.alpha_composite(o, (x, (b.height - o.height) // 2))
        x += o.width + 20
    b.alpha_composite(t, (x, 14))
    return shadow(b, 0.55, 10)


def pair(c, cx, cy, h, gap, j1, j2):
    put(c, jersey(j1, h, -7), cx - gap, cy)
    put(c, jersey(j2, h, 7), cx + gap, cy + 20)
    put(c, tag("$800"), cx - gap, cy + h * 0.56)
    put(c, tag("$400", "$800"), cx + gap, cy + h * 0.56 + 20)
    put(c, burst(int(h * 0.24), "-50%"), cx + gap + h * 0.40, cy - h * 0.43)
    plus = red("+", int(h * 0.32))
    put(c, plus, cx, cy + 10)


def post(name):
    W, H = 1080, 1350
    kicker, (j1, c1), (j2, c2) = DESIGNS[name]
    c = base(W, H, c1, c2)
    put(c, badge(120), 105, 125)
    put(c, pill("BLACK FRIDAY", 44, WHITE, (0, 0, 0)), W - 220, 125)
    put(c, white(kicker, 50, 0.04), W / 2, 255)
    put(c, white("2 JERSEYS POR", 96, 0.01), W / 2, 360)
    put(c, red("$1,200", 250, 0.0), W / 2, 530)
    pair(c, W / 2, 830, 330, 215, j1, j2)
    put(c, pill("LA 2DA AL 50% · AUTOMÁTICO EN EL CARRITO", 38), W / 2, 1185)
    put(c, white(f"{URL} · ENVÍO GRATIS · HASTA EL 30 DE NOV", 22, 0.08, "MontB.ttf"), W / 2, 1265)
    return c


def story(name):
    W, H = 1080, 1920
    kicker, (j1, c1), (j2, c2) = DESIGNS[name]
    c = base(W, H, c1, c2)
    put(c, badge(160), W / 2, 190)
    put(c, pill("BLACK FRIDAY", 52, WHITE, (0, 0, 0)), W / 2, 360)
    put(c, white(kicker, 56, 0.04), W / 2, 470)
    put(c, white("2 JERSEYS POR", 112, 0.01), W / 2, 590)
    put(c, red("$1,200", 300, 0.0), W / 2, 790)
    pair(c, W / 2, 1200, 400, 222, j1, j2)
    put(c, pill("LA 2DA AL 50% DE DESCUENTO", 52), W / 2, 1600)
    put(c, white("AUTOMÁTICO EN EL CARRITO · ENVÍO GRATIS", 28, 0.08, "MontB.ttf"), W / 2, 1695)
    put(c, white(f"{URL} · HASTA EL 30 DE NOV", 28, 0.08, "MontB.ttf"), W / 2, 1760)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n in DESIGNS:
        post(n).convert("RGB").save(f"{OUT}post-{n}.jpg", quality=94, subsampling=0)
        story(n).convert("RGB").save(f"{OUT}story-{n}.jpg", quality=94, subsampling=0)
    print("ok")
