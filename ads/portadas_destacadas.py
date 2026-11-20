"""Portadas de historias destacadas (1080x1920, contenido centrado en círculo) al estilo de la de 'PEDIDOS':
fondo negro, aro blanco, ícono blanco con líneas de velocidad rojas, título blanco en itálica, línea roja y logo.
Uso: python3 portadas_destacadas.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge

OUT = g.HERE + "out/destacadas/"
W, H = 1080, 1920
RED, WHITE = (226, 20, 32), (255, 255, 255)
CX, CY, R = W / 2, H / 2, 470


def italic(lay, k=0.22):
    w, h = lay.size
    return lay.transform((w + int(h * k), h), Image.AFFINE, (1, k, -h * k, 0, 1, 0), Image.BICUBIC)


def speed(d, x, y, n=3, gap=34, lens=(150, 110, 80)):
    for i in range(n):
        L = lens[i % len(lens)]
        d.rounded_rectangle([x - L, y + i * gap, x, y + i * gap + 12], radius=6, fill=RED)


def icon_shirt(d, cx, cy, s):
    pts = [(-0.42, -0.45), (-0.15, -0.5), (-0.07, -0.42), (0.07, -0.42), (0.15, -0.5), (0.42, -0.45), (0.62, -0.2),
           (0.46, -0.06), (0.34, -0.16), (0.34, 0.5), (-0.34, 0.5), (-0.34, -0.16), (-0.46, -0.06), (-0.62, -0.2)]
    P = [(cx + x * s, cy + y * s) for x, y in pts]
    d.polygon(P, outline=WHITE, width=16)
    for xx in (cx - 0.2 * s, cx + 0.2 * s):                    # fit lines
        for yy in range(int(cy - 0.05 * s), int(cy + 0.45 * s), 28):
            d.line([(xx, yy), (xx, yy + 14)], fill=RED, width=8)


def icon_card(d, cx, cy, s):
    w, h = s * 1.15, s * 0.75
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(s * 0.1), outline=WHITE, width=16)
    d.rectangle([cx - w / 2 + 8, cy - h / 2 + h * 0.2, cx + w / 2 - 8, cy - h / 2 + h * 0.38], fill=WHITE)
    d.rounded_rectangle([cx - w / 2 + s * 0.12, cy + h * 0.12, cx - w / 2 + s * 0.42, cy + h * 0.3], radius=8, fill=RED)


def cover(label, icon):
    c = Image.new("RGBA", (W, H), (14, 16, 22, 255))
    d = ImageDraw.Draw(c)
    d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=(6, 6, 8))
    d.ellipse([CX - R + 30, CY - R + 30, CX + R - 30, CY + R - 30], outline=WHITE, width=8)
    icon(d, CX + 20, CY - 140, 300)
    speed(d, CX - 190, CY - 200)
    t = italic(text(label, "Anton.ttf", 170, WHITE, 0.03))
    put(c, t, CX, CY + 110)
    d.line([(CX - 230, CY + 215), (CX + 230, CY + 215)], fill=RED, width=10)
    put(c, badge(130), CX, CY + 320)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, ic in (("GUÍA", icon_shirt), ("PAGOS", icon_card)):
        cover(name, ic).convert("RGB").save(OUT + f"portada-{name.lower().replace('í', 'i')}.jpg", quality=94, subsampling=0)
    print("ok")
