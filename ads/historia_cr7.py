"""Historia (1080x1920) despedida CR7 con Portugal: 'Se nos retira el 🐐 de Portugal · 2 x $1,000'.

Foto a sangre con degradados oscuros arriba (titular) y abajo (oferta + CTA + logo).
Uso: python3 historia_cr7.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from chat_doctor import emoji

PHOTO = g.HERE + "src/fotos/cr7_portugal.jpg"
OUT = g.HERE + "out/cr7/"
W, H = 1080, 1920
WHITE, GOLD = (255, 255, 255), (236, 196, 92)
PT_RED, PT_GREEN = (200, 16, 46), (0, 102, 51)


def base():
    im = Image.open(PHOTO).convert("RGB")
    s = W / im.width
    im = im.resize((W, round(im.height * s)), Image.LANCZOS)
    top = 200
    im = im.crop((0, top, W, top + H))
    a = np.asarray(im, np.float32)
    y = np.linspace(0, 1, H)[:, None, None]
    shade = np.clip(1 - 0.78 * np.clip((0.26 - y) / 0.26, 0, 1) ** 1.2 - 0.92 * np.clip((y - 0.58) / 0.27, 0, 1) ** 1.1, 0.08, 1)
    return Image.fromarray((a * shade).clip(0, 255).astype(np.uint8)).convert("RGBA")


def headline(c):
    l1 = text("SE NOS RETIRA EL", "Anton.ttf", 92, WHITE, 0.02)
    goat = emoji("🐐", 96)
    w = l1.width + 16 + goat.width
    x = (W - w) // 2
    c.alpha_composite(l1, (x, 160))
    c.alpha_composite(goat, (x + l1.width + 16, 160 + (l1.height - goat.height) // 2))
    put(c, text("DE PORTUGAL", "Anton.ttf", 132, GOLD, 0.03), W / 2, 330)


def flag_bar(c, y, w=360, h=8):
    x = (W - w) // 2
    d = ImageDraw.Draw(c)
    d.rectangle([x, y, x + w * 0.4, y + h], fill=PT_GREEN)
    d.rectangle([x + w * 0.4, y, x + w, y + h], fill=PT_RED)


def offer(c):
    put(c, text("POR SU HONOR", "MontB.ttf", 40, WHITE, 0.30), W / 2, 1385)
    put(c, text("2 X $1,000", "Anton.ttf", 210, WHITE, 0.01), W / 2, 1530)
    flag_bar(c, 1648)
    put(c, text("EN PLAYERAS DE PORTUGAL DE RONALDO", "MontB.ttf", 34, GOLD, 0.06), W / 2, 1700)
    put(c, text("PEDIDOS POR MENSAJE O EN FOOTBALLFRENZY.SHOP", "MontB.ttf", 26, WHITE, 0.05), W / 2, 1760)
    put(c, badge(104), W / 2, 1845)


def jersey(name, h, rot=0):
    im = Image.open(g.SRC + "portugal/" + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    p = 60
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p + 10, p + 20))
    a = a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.55))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out.rotate(rot, Image.BICUBIC, expand=True)


def stage():
    """Portugal-coloured backdrop: deep red, green glow bottom-left, gold glow behind the jerseys."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rgb = np.ones((H, W, 3), np.float32) * np.array([92, 8, 18], np.float32)
    def glow(cx, cy, r, col, k):
        g_ = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2)))[..., None]
        return g_ * (np.array(col, np.float32) - rgb) * k
    rgb = rgb + glow(W * 0.5, H * 0.50, 420, (210, 40, 50), 0.55)
    rgb = rgb + glow(-100, H * 1.0, 600, (0, 90, 45), 0.85)
    rgb = rgb + glow(W + 100, -100, 520, (0, 90, 45), 0.55)
    v = np.linspace(0, 1, H)[:, None, None]
    rgb = rgb * (1 - 0.55 * np.clip((v - 0.62) / 0.38, 0, 1)) + np.random.default_rng(3).normal(0, 2, (H, W, 1))
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")


def build_producto():
    """Versión para anuncio pagado: sin foto del jugador, solo jerseys de la tienda."""
    c = stage()
    headline(c)
    put(c, jersey("pt_eusebio.png", 470, 8), W / 2 - 265, 820)
    put(c, jersey("pt2026_home.png", 470, -8), W / 2 + 265, 820)
    put(c, jersey("pt2004_cr7.png", 620), W / 2, 900)
    offer(c)
    return c


def build():
    c = base()
    headline(c)
    offer(c)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "story-cr7-2x1000.jpg", quality=94, subsampling=0)
    build_producto().convert("RGB").save(OUT + "story-cr7-2x1000-producto.jpg", quality=94, subsampling=0)
    print("ok")
