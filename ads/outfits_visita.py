"""Carrusel 'Outfits con la de visita' (5 slides 1080x1350) adaptado a la marca, sin promos.
Se borra el título original (inpainting sobre el fondo gris) y se rotula con tipografía y logo de Football Frenzy.
Uso: python3 outfits_visita.py
"""
import os
import cv2
import numpy as np
from PIL import Image
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from buenfin_logo import shadow
from buenfin_2da50 import pill, RED, WHITE

SRC, OUT = g.SRC + "outfits_ref/", g.HERE + "out/outfits_visita/"
W, H = 1080, 1350
CLUBS = ["REAL MADRID", "CHIVAS", "CRUZ AZUL", "JUVENTUS", "AC MILAN"]


def clean(n):
    a = cv2.imread(f"{SRC}{n}.jpg")
    h = a.shape[0]
    band = a[70:285].astype(int)
    m = np.zeros(a.shape[:2], np.uint8)
    m[70:285] = ((band.min(axis=2) > 200)).astype(np.uint8) * 255      # white title letters
    m = cv2.dilate(m, np.ones((11, 11), np.uint8))
    a = cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA)
    y0 = max(0, h - round(1179 * 1.25) - 10)
    a = a[y0:y0 + round(1179 * 1.25)]
    im = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB)).resize((W, H), Image.LANCZOS).convert("RGBA")
    return im, y0


def slide(i, club):
    c, y0 = clean(i + 1)
    s = W / 1179
    yt = (175 - y0) * s                                   # where the old title sat
    put(c, pill("OUTFIT CON LA DE VISITA", 30), W / 2, yt - 72)
    put(c, shadow(text(club, "Anton.ttf", 118, WHITE, 0.02), 0.45, 14), W / 2, yt + 22)
    put(c, badge(90), 64, H - 62)
    put(c, shadow(text(f"{i + 1}/5", "MontB.ttf", 26, WHITE, 0.05), 0.5, 6), W - 60, H - 40)
    put(c, shadow(text("FOOTBALLFRENZY.SHOP", "MontB.ttf", 24, WHITE, 0.12), 0.5, 6), W / 2, H - 34)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i, club in enumerate(CLUBS):
        slide(i, club).convert("RGB").save(f"{OUT}{i + 1:02d}.jpg", quality=93, subsampling=0)
    print("ok")
