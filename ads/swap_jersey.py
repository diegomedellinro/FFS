"""Cambia la jersey de un flat-lay de outfits (él/ella) por otra jersey recortada, sin IA de pago.

Borra la jersey original (inpainting con el concreto del fondo), pega la nueva escalada a la misma caja y le agrega
una sombra suave. Las cajas están en coordenadas de las imágenes base (1792x2240).
"""
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps

BASES = {
    "fcb": {"src": "out/outfits/raw/barca-golf.png", "boxes": [(240, 400, 900, 965), (956, 478, 1522, 912)],
            "keep": [(90, 700, 300, 830)]},
    "rm": {"src": "out/outfits/raw/real-madrid.png", "boxes": [(186, 358, 892, 812), (968, 428, 1552, 812)],
           "keep": [(90, 760, 330, 860)]},
}


def _bg_mask(rgb, box, tol=34):
    """Pixels inside box that differ from the smooth concrete background (= the old jersey)."""
    border = np.concatenate([rgb[:40].reshape(-1, 3), rgb[:, :40].reshape(-1, 3), rgb[:, -40:].reshape(-1, 3)])
    bg = np.median(border, 0)
    d = (np.abs(rgb.astype(np.int16) - bg).max(2) > tol).astype(np.uint8)
    m = np.zeros(d.shape, np.uint8)
    x0, y0, x1, y1 = box
    m[y0:y1, x0:x1] = d[y0:y1, x0:x1]
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        m = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    ff = m.copy()
    cv2.floodFill(ff, None, (0, 0), 1)
    m = m | (1 - ff)
    return cv2.dilate(m, np.ones((11, 11), np.uint8))


def _place(canvas, jersey, box, pad=1.07):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    s = max(bw * pad / jersey.width, bh * 1.0 / jersey.height)
    j = jersey.resize((round(jersey.width * s), round(jersey.height * s)), Image.LANCZOS)
    x = (x0 + x1) // 2 - j.width // 2
    y = y0 - 10
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    a = Image.new("L", canvas.size, 0)
    a.paste(j.getchannel("A"), (x + 6, y + 12))
    a = a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.32))
    sh.putalpha(a)
    canvas.alpha_composite(sh)
    canvas.alpha_composite(j, (x, y))


def swap(base, jersey_png, out_png, flip=False):
    info = BASES[base]
    im = Image.open(info["src"]).convert("RGB")
    rgb = np.asarray(im).copy()
    mask = np.zeros(rgb.shape[:2], np.uint8)
    for b in info["boxes"]:
        mask |= _bg_mask(rgb, (b[0] - 40, b[1] - 20, b[2] + 40, b[3] + 5))
    for x0, y0, x1, y1 in info.get("keep", []):
        mask[y0:y1, x0:x1] = 0
    clean = cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask * 255, 9, cv2.INPAINT_TELEA)
    canvas = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)).convert("RGBA")
    boxes = info["boxes"]
    if flip:
        canvas = ImageOps.mirror(canvas)
        W = canvas.width
        boxes = [(W - b[2], b[1], W - b[0], b[3]) for b in boxes]
    jersey = Image.open(jersey_png).convert("RGBA")
    for b in boxes:
        _place(canvas, jersey, b)
    canvas.convert("RGB").save(out_png)
    return out_png


if __name__ == "__main__":
    swap("fcb", "src/outfit/psg.png", "out/outfits/raw/psg.png")
    swap("rm", "src/outfit/miami.png", "out/outfits/raw/inter-miami.png")
    swap("fcb", "src/outfit/america.png", "out/outfits/raw/america.png", flip=True)
    print("ok")
