"""Buen Fin: 'Compra una jersey y llévate la 2da al 50%' con código BUENFIN. Post 1080x1350 + historia 1080x1920.
Estilo de marca (negro, brillo rojo, grano). Uso: python3 buenfin_2da50.py
"""
import math
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text, background
from hf_ads import badge
from buenfin_logo import jersey, shadow

OUT = g.HERE + "out/buenfin_2da50/"
RED, RED2, WHITE, GREY = (226, 20, 32), (150, 10, 18), (255, 255, 255), (170, 170, 176)
PAIR = [("rm1415_third_ls.png", -6), ("psg_home26.png", 6)]


def bg(W, H):
    c = background(W, H, glows=((0.5, 0.6, 0.8, RED2, 0.75), (0.5, 0.05, 0.5, RED2, 0.3))).copy()
    d = ImageDraw.Draw(c)
    for y in (60, H - 60):
        d.line([(60, y), (W - 60, y)], fill=RED + (255,), width=3)
    return c


def red(s, px, track=0.0):
    return shadow(text(s, "Anton.ttf", px, RED, track), 0.6, 12)


def white(s, px, track=0.0, font="Anton.ttf", col=WHITE):
    return shadow(text(s, font, px, col, track), 0.6, 10)


def pill(s, px, fg=WHITE, bg_=RED, strike=None):
    t = text(s, "Anton.ttf", px, fg, 0.02, strike=strike) if strike else text(s, "Anton.ttf", px, fg, 0.02)
    b = Image.new("RGBA", (t.width + 60, t.height + 28), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, b.width - 1, b.height - 1], radius=b.height // 2, fill=bg_ + (255,))
    b.alpha_composite(t, (30, 14))
    return b


def burst(r, label="-50%"):
    im = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0))
    pts = []
    for i in range(32):
        a = i * math.pi / 16
        rr = r if i % 2 == 0 else r * 0.86
        pts.append((r + 10 + rr * math.cos(a), r + 10 + rr * math.sin(a)))
    d = ImageDraw.Draw(im)
    d.polygon(pts, fill=RED + (255,))
    d.ellipse([r + 10 - r * 0.74, r + 10 - r * 0.74, r + 10 + r * 0.74, r + 10 + r * 0.74], outline=WHITE + (255,), width=4)
    t = text(label, "Anton.ttf", int(r * 0.62), WHITE, 0.0)
    im.alpha_composite(t, ((im.width - t.width) // 2, (im.height - t.height) // 2))
    return shadow(im.rotate(-12, Image.BICUBIC), 0.6, 12)


def code_box(px):
    t1 = text("USA EL CÓDIGO", "MontB.ttf", int(px * 0.42), GREY, 0.12)
    t2 = text("BUENFIN", "Anton.ttf", px, WHITE, 0.08)
    w = max(t1.width, t2.width) + 120
    h = t1.height + t2.height + 70
    b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=26, fill=(14, 14, 16, 235))
    x = 0                                                     # dashed red border
    seg = 26
    for x in range(20, w - 20, seg * 2):
        d.line([(x, 3), (min(x + seg, w - 20), 3)], fill=RED + (255,), width=6)
        d.line([(x, h - 4), (min(x + seg, w - 20), h - 4)], fill=RED + (255,), width=6)
    for y in range(20, h - 20, seg * 2):
        d.line([(3, y), (3, min(y + seg, h - 20))], fill=RED + (255,), width=6)
        d.line([(w - 4, y), (w - 4, min(y + seg, h - 20))], fill=RED + (255,), width=6)
    b.alpha_composite(t1, ((w - t1.width) // 2, 26))
    b.alpha_composite(t2, ((w - t2.width) // 2, 26 + t1.height + 16))
    return b


def pair(c, cy, h, gap):
    W = c.width
    (a, ra), (b_, rb) = PAIR
    put(c, jersey(a, h, ra), W / 2 - gap, cy)
    put(c, jersey(b_, h, rb), W / 2 + gap, cy + 20)
    put(c, pill("$800", int(h * 0.13)), W / 2 - gap, cy + h * 0.55)
    put(c, pill("$400", int(h * 0.13)), W / 2 + gap, cy + h * 0.55 + 20)
    put(c, burst(int(h * 0.27)), W / 2 + gap + h * 0.42, cy - h * 0.42)
    put(c, red("+", int(h * 0.3)), W / 2, cy + 10)


def post():
    W, H = 1080, 1350
    c = bg(W, H)
    put(c, badge(130), 130, 140)
    put(c, pill("BUEN FIN · 13 AL 17 NOV", 38), W - 290, 140)
    put(c, white("COMPRA UNA Y LLÉVATE", 80, 0.01), W / 2, 265)
    put(c, red("LA 2DA AL 50%", 160, 0.01), W / 2, 395)
    pair(c, 735, 320, 225)
    put(c, code_box(84), W / 2, 1125)
    put(c, white("FOOTBALLFRENZY.SHOP · ENVÍO GRATIS A TODO MÉXICO", 24, 0.08, "MontB.ttf"), W / 2, 1260)
    return c


def story():
    W, H = 1080, 1920
    c = bg(W, H)
    put(c, badge(200), W / 2, 260)
    put(c, pill("BUEN FIN · 13 AL 17 DE NOVIEMBRE", 42), W / 2, 450)
    put(c, white("COMPRA UNA Y LLÉVATE", 96, 0.01), W / 2, 590)
    put(c, red("LA 2DA", 220, 0.01), W / 2, 770)
    put(c, red("AL 50%", 220, 0.01), W / 2, 960)
    pair(c, 1290, 360, 225)
    put(c, code_box(96), W / 2, 1680)
    put(c, white("FOOTBALLFRENZY.SHOP · ENVÍO GRATIS · PIDE POR DM", 28, 0.08, "MontB.ttf"), W / 2, 1828)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    post().convert("RGB").save(OUT + "post-2da-al-50.jpg", quality=94, subsampling=0)
    story().convert("RGB").save(OUT + "story-2da-al-50.jpg", quality=94, subsampling=0)
    print("ok")
