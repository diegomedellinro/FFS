"""Creativos Buen Fin con el logo oficial (src/buenfin/logo.png): post 1080x1350, historia 1080x1920
(estadio azul con dorado, como el video) y una versión clara del post.

Uso: python3 buenfin_logo.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text, RED
from hf_ads import badge

OUT = g.HERE + "out/buenfin_logo/"
LOGO = Image.open(g.SRC + "buenfin/logo.png").convert("RGBA")
NAVY, NAVY2 = (14, 26, 58), (6, 12, 30)
CREAM, GOLD, WHITE, INK = (246, 236, 214), (226, 190, 110), (255, 255, 255), (15, 15, 18)
FIVE = [("fcb_0809_home.png", 0.80, 8), ("viejo/ame1213.png", 0.9, 4), ("spotify/golf.png", 1.0, 0),
        ("mex_gold.png", 0.9, -4), ("cl_rm_away26.png", 0.80, -8)]


def stadium(W, H):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / H
    img = np.array(NAVY, np.float32) * (1 - t[..., None]) + np.array(NAVY2, np.float32) * t[..., None]
    for cx in (0.18, 0.5, 0.82):
        w = 0.10 + 0.55 * t
        a = np.clip(1 - np.abs(xx / W - cx) / w, 0, 1) ** 2 * (1 - t) ** 1.4 * 0.33
        img = img + a[..., None] * 255 * np.array([0.55, 0.65, 0.95])
    v = np.sqrt(((xx / W - 0.5) * 1.2) ** 2 + ((yy / H - 0.5) * 1.0) ** 2)
    img = img * (1 - 0.55 * np.clip(v - 0.25, 0, 1)[..., None]) + np.random.default_rng(1).normal(0, 2.5, (H, W, 1))
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")


def light(W, H):
    yy = np.linspace(0, 1, H)[:, None]
    v = 252 - 12 * yy ** 2 + np.random.default_rng(2).normal(0, 0.8, (H, W))
    return Image.fromarray(np.dstack([v, v, v]).clip(0, 255).astype(np.uint8)).convert("RGBA")


def shadow(lay, k=0.5, r=10, col=(0, 0, 10)):
    p = r * 3
    out = Image.new("RGBA", (lay.width + 2 * p, lay.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(lay.getchannel("A"), (p, p + r // 2))
    a = a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * k))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, col + (255,)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(lay, (p, p))
    return out


def gold(s, px, track=0.0):
    lay = text(s, "Anton.ttf", px, WHITE, track)
    t = np.linspace(0, 1, lay.height)[:, None, None]
    rgb = np.array((248, 222, 160), np.float32) * (1 - t) + np.array((196, 150, 70), np.float32) * t
    out = Image.fromarray(np.broadcast_to(rgb, (lay.height, lay.width, 3)).astype(np.uint8)).convert("RGBA")
    out.putalpha(lay.getchannel("A"))
    return shadow(out)


def logo(w):
    return shadow(LOGO.resize((w, round(LOGO.height * w / LOGO.width)), Image.LANCZOS), 0.45, 14)


def jersey(name, h, rot, dark=True):
    im = Image.open(g.SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    p = 50
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p + 8, p + 18))
    a = a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * (0.6 if dark else 0.3)))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 8, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out.rotate(rot, Image.BICUBIC, expand=True)


def fan(c, cy, h, spread, dark=True):
    W = c.width
    xs = [W / 2 + spread * k for k in (-2, -1, 0, 1, 2)]
    order = [0, 4, 1, 3, 2]                      # sides first, centre last (on top)
    for i in order:
        n, k, r = FIVE[i]
        put(c, jersey(n, int(h * k), r, dark), xs[i], cy + (1 - k) * h * 0.35)


def pill(s, px, fg, bg):
    t = text(s, "Anton.ttf", px, fg, 0.02)
    b = Image.new("RGBA", (t.width + 60, t.height + 28), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, b.width - 1, b.height - 1], radius=b.height // 2, fill=bg + (255,))
    b.alpha_composite(t, (30, 14))
    return b


def offers(c, y, scale=1.0, dark=True):
    """'3x2' | '5x3' side by side with their prices."""
    W = c.width
    big = gold if dark else (lambda s, px: shadow(text(s, "Anton.ttf", px, RED, 0.0), 0.25, 8))
    sub_col = CREAM if dark else INK
    for x, b, s in ((W * 0.28, "3x2", "3 POR $1,600"), (W * 0.72, "5x3", "5 POR $2,400")):
        put(c, big(b, int(230 * scale)), x, y)
        put(c, text(s, "Anton.ttf", int(52 * scale), sub_col, 0.03), x, y + 165 * scale)
    d = ImageDraw.Draw(c)
    d.line([(W / 2, y - 110 * scale), (W / 2, y + 190 * scale)], fill=GOLD if dark else RED, width=4)


def post_dark():
    W, H = 1080, 1350
    c = stadium(W, H)
    put(c, logo(300), W / 2, 200)
    offers(c, 520)
    fan(c, 935, 370, 178)
    put(c, pill("AUTOMÁTICO EN EL CARRITO · ENVÍO GRATIS", 40, NAVY2, CREAM), W / 2, 1185)
    put(c, badge(90), W - 85, H - 70)
    put(c, text("FOOTBALLFRENZY.SHOP · PIDE POR DM", "MontB.ttf", 24, CREAM, 0.08), W / 2 - 30, H - 70)
    return c


def story_dark():
    W, H = 1080, 1920
    c = stadium(W, H)
    put(c, logo(400), W / 2, 420)
    offers(c, 830, 1.1)
    fan(c, 1290, 400, 178)
    put(c, pill("AUTOMÁTICO EN EL CARRITO · ENVÍO GRATIS", 42, NAVY2, CREAM), W / 2, 1570)
    put(c, text("HASTA EL 1 DE DICIEMBRE", "Anton.ttf", 50, GOLD, 0.05), W / 2, 1660)
    put(c, badge(110), W / 2 - 300, 1770)
    put(c, text("FOOTBALLFRENZY.SHOP · DM", "MontB.ttf", 30, CREAM, 0.08), W / 2 + 60, 1770)
    return c


def post_light():
    W, H = 1080, 1350
    c = light(W, H)
    put(c, logo(280), 230, 200)
    put(c, shadow(text("EN FOOTBALL", "Anton.ttf", 92, INK, 0.0), 0.2, 6), 730, 150)
    put(c, shadow(text("FRENZY", "Anton.ttf", 92, RED, 0.0), 0.2, 6), 730, 255)
    offers(c, 520, 1.0, dark=False)
    fan(c, 935, 370, 178, dark=False)
    put(c, pill("AUTOMÁTICO EN EL CARRITO · ENVÍO GRATIS", 40, WHITE, RED), W / 2, 1185)
    put(c, badge(90), W - 85, H - 70)
    put(c, text("FOOTBALLFRENZY.SHOP · PIDE POR DM", "MontB.ttf", 24, INK, 0.08), W / 2 - 30, H - 70)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("post-azul", post_dark), ("story-azul", story_dark), ("post-claro", post_light)):
        fn().convert("RGB").save(f"{OUT}{name}.jpg", quality=94, subsampling=0)
    print("ok")
