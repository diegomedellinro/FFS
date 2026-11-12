"""Quita los elementos de la interfaz de Instagram (contador, avatar, ícono de perfil y de volumen) de capturas.
Uso: python3 limpiar_ig.py
"""
import cv2
import numpy as np
import generar_ads as g

SRC, OUT = g.SRC + "fotos/rm1415/", g.HERE + "out/rm1415_fotos/"
# (x0, y0, x1, y1) rects and (cx, cy, r) circles; y < 0 means from the bottom
JOBS = {
    2: ([(994, 12, 1152, 110)], [(113, 1302, 84), (163, 1362, 54), (80, 1471, 50), (1097, 1471, 50)]),
}
CROPS = {1: (118, 1368), 3: (118, 1352)}      # floor photos: crop off the UI bands (y0, y1), jersey untouched

for n, (rects, circles) in JOBS.items():
    im = cv2.imread(f"{SRC}{n}.jpg")
    h = im.shape[0]
    m = np.zeros(im.shape[:2], np.uint8)
    for x0, y0, x1, y1 in rects:
        cv2.rectangle(m, (x0, y0), (x1, y1), 255, -1)
    for cx, cy, r in circles:
        cv2.circle(m, (cx, cy), r, 255, -1)
    out = cv2.inpaint(im, m, 9, cv2.INPAINT_TELEA)
    # add back a little grain so the patches don't look smooth
    noise = np.random.default_rng(n).normal(0, 3, im.shape).astype(np.float32)
    k = cv2.GaussianBlur(m, (31, 31), 0)[..., None] / 255.0
    out = np.clip(out + noise * k, 0, 255).astype(np.uint8)
    cv2.imwrite(f"{OUT}rm1415-{n}.jpg", out, [cv2.IMWRITE_JPEG_QUALITY, 95])
for n, (y0, y1) in CROPS.items():
    im = cv2.imread(f"{SRC}{n}.jpg")
    cv2.imwrite(f"{OUT}rm1415-{n}.jpg", im[y0:y1], [cv2.IMWRITE_JPEG_QUALITY, 95])
print("ok")
