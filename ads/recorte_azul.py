"""Recorta jerseys fotografiadas sobre fondo azul liso (conserva logos/escudos): clave de color + región conectada al borde."""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def cut(src, dst, tol=95, corners_only=False):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    border = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    d = np.sqrt(((a - bg) ** 2).sum(axis=2))
    lab, _ = ndimage.label(d < tol)
    if corners_only:
        edge = {lab[2, 2], lab[2, -3], lab[-3, 2], lab[-3, -3]} - {0}
    else:
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    back = np.isin(lab, list(edge))
    fg = ~back
    lab2, n = ndimage.label(fg)
    if n:
        fg = lab2 == (np.bincount(lab2.ravel())[1:].argmax() + 1)
    fg = ndimage.binary_fill_holes(fg)
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    # despill: pull blue fringe toward neutral near the edge
    rgb = a.copy()
    edge_band = (np.asarray(alpha) > 0) & (np.asarray(alpha.filter(ImageFilter.MinFilter(7))) < 255)
    spill = np.clip(rgb[..., 2] - np.maximum(rgb[..., 0], rgb[..., 1]), 0, None)
    rgb[..., 2] = np.where(edge_band, rgb[..., 2] - spill * 0.8, rgb[..., 2])
    out = Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(alpha)
    out = out.crop(out.getchannel("A").getbbox())
    out.save(dst)
    print(dst, out.size, bg)


if __name__ == "__main__":
    cut(sys.argv[1], sys.argv[2], corners_only="--corners" in sys.argv)
