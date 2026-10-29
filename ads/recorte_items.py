"""Separa prendas/accesorios de un flat-lay sobre fondo liso (concreto): cada objeto -> PNG transparente.
Uso: python3 recorte_items.py imagen.png carpeta_salida
"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def items(src, out, tol=26, min_area=1500):
    os.makedirs(out, exist_ok=True)
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    # background estimate: heavy median blur of the image (concrete is smooth), objects stand out from it
    bgimg = np.asarray(im.resize((im.width // 16, im.height // 16)).filter(ImageFilter.MedianFilter(9)).resize(im.size, Image.BILINEAR), np.float32)
    d = np.abs(a - bgimg).max(axis=2)
    fg = d > tol
    fg = ndimage.binary_closing(fg, iterations=4)
    fg = ndimage.binary_fill_holes(fg)
    fg = ndimage.binary_opening(fg, iterations=2)
    lab, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    res = []
    for i, s in enumerate(sizes, 1):
        if s < min_area:
            continue
        m = lab == i
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        alpha = Image.fromarray((m[y0:y1, x0:x1] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
        piece = im.crop((x0, y0, x1, y1)).convert("RGBA")
        piece.putalpha(alpha)
        name = f"{out}/{i:03d}_{x0}_{y0}.png"
        piece.save(name)
        res.append((name, x0, y0, x1 - x0, y1 - y0, int(s)))
    for r in sorted(res, key=lambda r: (r[2], r[1])):
        print(*r)


if __name__ == "__main__":
    items(sys.argv[1], sys.argv[2])
