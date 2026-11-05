"""Historia (1080x1920) despedida CR7 con Portugal: 'Se nos retira el 🐐 de Portugal · 2 x $1,000'.

Foto a sangre con degradados oscuros arriba (titular) y abajo (oferta + CTA + logo).
Uso: python3 historia_cr7.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw
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


def build():
    c = base()
    headline(c)
    offer(c)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "story-cr7-2x1000.jpg", quality=94, subsampling=0)
    print("ok")
