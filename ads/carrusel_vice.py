"""Carrusel 'estilo Vice City' (1080x1350): las 4 ilustraciones del usuario solo con el logo de Football Frenzy
(se quitan los íconos de Instagram) + slide final propio con fondo atardecer neón y CTA.
Uso: python3 carrusel_vice.py
"""
import math
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from buenfin_logo import jersey, shadow
from buenfin_2da50 import pill

SRC, OUT = g.SRC + "vice/", g.HERE + "out/carrusel_vice/"
W, H = 1080, 1350
UI = {  # counter box (or None) and mute-button centre, in source pixels
    1: (None, (1097, 1467)), 2: ((1000, 24, 1144, 108), (1097, 1474)),
    3: ((1000, 24, 1144, 108), (1097, 1470)), 4: ((1000, 26, 1144, 112), (1097, 1478)),
}


def clean(n):
    a = cv2.imread(f"{SRC}{n}.jpg")
    m = np.zeros(a.shape[:2], np.uint8)
    box, (mx, my) = UI[n]
    if box:
        cv2.rectangle(m, box[:2], box[2:], 255, -1)
    cv2.circle(m, (mx, my), 52, 255, -1)
    a = cv2.inpaint(a, m, 11, cv2.INPAINT_TELEA).astype(np.float32)
    k = (cv2.GaussianBlur(m, (25, 25), 0) / 255.0)[..., None]
    a += np.random.default_rng(n).normal(0, 6, a.shape).astype(np.float32) * k     # match the film grain
    a = np.clip(a, 0, 255).astype(np.uint8)
    nw = round(a.shape[1] * H / a.shape[0])                    # fit full height, extend the sides
    a = cv2.resize(a, (nw, H), interpolation=cv2.INTER_LANCZOS4)
    l = (W - nw) // 2
    a = cv2.copyMakeBorder(a, 0, 0, l, W - nw - l, cv2.BORDER_REPLICATE)
    return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB)).convert("RGBA")


def slide(n):
    c = clean(n)
    put(c, badge(120), W - 90, H - 90)
    return c


# ---------------------------------------------------------------- final slide
def neon(s, px, col, glow=(255, 60, 180), font="Anton.ttf", track=0.02):
    t = text(s, font, px, col, track)
    p = 40
    out = Image.new("RGBA", (t.width + 2 * p, t.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(t.getchannel("A"), (p, p))
    for r, k in ((22, 0.9), (8, 1.0)):
        g_ = a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, int(v * k * 1.6)))
        out.alpha_composite(Image.composite(Image.new("RGBA", out.size, glow + (255,)), Image.new("RGBA", out.size, (0, 0, 0, 0)), g_))
    out.alpha_composite(t, (p, p))
    return out


def palm(d, x, y, s, col):
    pts = [(x + math.sin(i / 12) * 18 * s, y - i * 9 * s) for i in range(40)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.line([(x0, y0), (x1, y1)], fill=col, width=int(16 * s))
    tx, ty = pts[-1]
    for ang in range(-170, 10, 30):
        for j in range(26):
            a = math.radians(ang + j * 1.2)
            r = j * 7 * s
            d.ellipse([tx + math.cos(a) * r - 9 * s, ty + math.sin(a) * r * 0.7 + j * j * 0.35 * s - 9 * s,
                       tx + math.cos(a) * r + 9 * s, ty + math.sin(a) * r * 0.7 + j * j * 0.35 * s + 9 * s], fill=col)


def vice_bg():
    yy = np.linspace(0, 1, H)[:, None, None]
    top, mid, low = np.array([38, 18, 82]), np.array([214, 70, 150]), np.array([255, 160, 90])
    sky = np.where(yy < 0.55, top + (mid - top) * (yy / 0.55), mid + (low - mid) * ((yy - 0.55) / 0.45))
    img = np.broadcast_to(sky, (H, W, 3)).astype(np.float32).copy()
    c = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(c)
    # striped sun
    cx, cy, r = W / 2, 930, 300
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sun)
    ds.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 205, 110, 255))
    for k in range(8):
        y0 = cy + 40 + k * 32
        ds.rectangle([0, y0, W, y0 + 6 + k * 2], fill=(0, 0, 0, 0))
    c.alpha_composite(sun)
    # sea + neon grid
    sea_y = 1040
    d.rectangle([0, sea_y, W, H], fill=(30, 12, 60, 255))
    for k in range(14):
        y = sea_y + (k ** 1.8) * 1.6
        d.line([(0, y), (W, y)], fill=(255, 70, 190, 150), width=2)
    for k in range(-14, 15):
        d.line([(cx + k * 30, sea_y), (cx + k * 160, H)], fill=(255, 70, 190, 120), width=2)
    # city silhouette + palms
    rng = np.random.default_rng(3)
    x = 0
    while x < W:
        bw, bh = rng.integers(40, 110), rng.integers(60, 240)
        if abs(x - cx) > 260:
            d.rectangle([x, sea_y - bh, x + bw, sea_y], fill=(48, 16, 70, 255))
        x += bw + 6
    palm(d, 90, sea_y + 10, 1.25, (24, 8, 40, 255))
    palm(d, W - 110, sea_y + 10, 1.05, (24, 8, 40, 255))
    return c


def final():
    c = vice_bg()
    put(c, badge(150), W / 2, 140)
    put(c, neon("CONSIGUE LA JERSEY", 104, (255, 255, 255)), W / 2, 330)
    put(c, neon("DE ESTOS EQUIPOS", 104, (255, 235, 245), glow=(80, 200, 255)), W / 2, 450)
    names = [("psg_home26.png", -8), ("cl_fcb_home26.png", -3), ("bayern.png", 3), ("rm_home26_v2.png", 8)]
    for i, (n, r) in enumerate(names):
        put(c, jersey(n, 300, r), W / 2 + (i - 1.5) * 238, 760 + (abs(i - 1.5) < 1) * -30)
    put(c, pill("PIDE YA EN FOOTBALLFRENZY.SHOP", 52), W / 2, 1150)
    put(c, shadow(text("O MÁNDANOS DM · ENVÍO GRATIS A TODO MÉXICO", "MontB.ttf", 28, (255, 255, 255), 0.06), 0.6, 8), W / 2, 1245)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n in range(1, 5):
        slide(n).convert("RGB").save(f"{OUT}{n:02d}.jpg", quality=93, subsampling=0)
    final().convert("RGB").save(f"{OUT}05.jpg", quality=93, subsampling=0)
    print("ok")
