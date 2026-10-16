"""Recorta productos sobre fondo liso (blanco/gris) por relleno desde los bordes. usage: cutout.py in out.png"""
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

def cutout(path, tol=26):
    im = Image.open(path).convert('RGB'); a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    near = np.abs(a - bg).max(axis=2) <= tol
    lab, _ = ndimage.label(near)
    edge_labels = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    edge_labels = edge_labels[edge_labels > 0]
    bgmask = np.isin(lab, edge_labels)
    fg = ~bgmask
    fg = ndimage.binary_opening(fg, iterations=1)
    fg = ndimage.binary_fill_holes(fg)
    # keep only big components (drops dust / stray specks)
    lab2, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab2, range(1, n + 1)); keep = sizes >= sizes.max() * 0.04
        fg = np.isin(lab2, np.nonzero(keep)[0] + 1)
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
    out = im.convert('RGBA'); out.putalpha(alpha)
    return out.crop(out.getbbox())

if __name__ == '__main__':
    cutout(sys.argv[1]).save(sys.argv[2]); print('ok')
