"""Historia 'Métodos de pago' (1080x1920): Mercado Pago, transferencia, depósito en OXXO y Apple Pay.
Uso: python3 historia_pagos.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from chat_doctor import emoji
from buenfin_2da50 import bg, red, white, pill, RED, GREY, WHITE

OUT = g.HERE + "out/pagos/"
W, H = 1080, 1920
METODOS = [
    ("💳", "MERCADO PAGO", "CON TU CUENTA O TARJETA"),
    ("🏦", "TRANSFERENCIA", "TE PASAMOS LOS DATOS POR DM"),
    ("🏪", "DEPÓSITO EN OXXO", "PAGA EN EFECTIVO EN CUALQUIER OXXO"),
    ("📱", "APPLE PAY", "PAGA EN SEGUNDOS DESDE TU IPHONE"),
]


def card(ico, name, sub, w=960, h=200):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=(18, 18, 21, 240), outline=(80, 22, 26, 255), width=2)
    d.ellipse([36, h / 2 - 66, 168, h / 2 + 66], fill=RED + (255,))
    e = emoji(ico, 76)
    c.alpha_composite(e, (102 - e.width // 2, h // 2 - e.height // 2))
    t = text(name, "Anton.ttf", 70, WHITE, 0.01)
    s = text(sub, "MontB.ttf", 24, GREY, 0.08)
    c.alpha_composite(t, (220, h // 2 - t.height + 8))
    c.alpha_composite(s, (222, h // 2 + 22))
    return c


def story():
    c = bg(W, H)
    put(c, badge(150), W / 2, 170)
    put(c, white("¿CÓMO PUEDES PAGAR?", 52, 0.06, "MontB.ttf"), W / 2, 330)
    put(c, white("MÉTODOS", 145, 0.01), W / 2, 460)
    put(c, red("DE PAGO", 145, 0.01), W / 2, 615)
    for i, m in enumerate(METODOS):
        put(c, card(*m), W / 2, 830 + i * 220)
    put(c, white("TAMBIÉN TARJETA DE CRÉDITO Y DÉBITO", 30, 0.08, "MontB.ttf"), W / 2, 1665)
    put(c, pill("PAGO 100% SEGURO · FOOTBALLFRENZY.SHOP", 42), W / 2, 1765)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    story().convert("RGB").save(OUT + "story-metodos-de-pago.jpg", quality=94, subsampling=0)
    print("ok")
