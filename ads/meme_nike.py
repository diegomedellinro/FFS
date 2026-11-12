"""Post meme 'Papá, Nike es mejor que Adidas' (1080x1350), traducido al español.
Uso: python3 meme_nike.py
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import generar_ads as g
from generar_ads import put
from hf_ads import badge

OUT = g.HERE + "out/meme_nike/"
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"


def clean(a):
    lum = a.mean(axis=2)
    # --- speech bubble: fit the outline ellipse from edge points, whiten the inside, patch the '1/8' pill
    pts = []
    for x in list(range(840, 1150, 6)):
        ys = np.nonzero(lum[200:330, x] < 90)[0]
        if len(ys):
            pts.append((x, 200 + ys[0]))
    for y in range(60, 220, 6):
        xs = np.nonzero(lum[y, 620:672] < 90)[0]
        if len(xs):
            pts.append((620 + xs[0], y))
        xs = np.nonzero(lum[y, 1140:1175] < 90)[0]
        if len(xs):
            pts.append((1140 + xs[-1], y))
    E = cv2.fitEllipse(np.array(pts, np.float32))
    (cx, cy), (aw, ah), ang = E
    inside = np.zeros(lum.shape, np.uint8)
    cv2.ellipse(inside, ((cx, cy), (aw - 18, ah - 18), ang), 1, -1)
    a[inside == 1] = 254
    full = np.zeros(lum.shape, np.uint8)
    cv2.ellipse(full, E, 1, -1)
    px0, py0, px1, py1 = 1025, 18, 1160, 100
    sky = np.median(a[5:25, 1150:1172].reshape(-1, 3), axis=0)
    box = np.zeros(lum.shape, bool)
    box[py0:py1, px0:px1] = True
    a[box & (full == 1)] = 254
    a[box & (full == 0)] = sky
    arc = np.zeros_like(a)
    cv2.ellipse(arc, E, (255, 255, 255), 5, cv2.LINE_AA)
    k = (arc[..., 0] / 255.0)[..., None] * box[..., None]
    a[:] = (a * (1 - k) + 10 * k).astype(np.uint8)
    # --- bottom caption: per-row background colour from the clean part of the row
    ty0, ty1, tx0, tx1 = 982, 1148, 552, 932
    reg = a[ty0 - 12:ty1 + 12, tx0 - 10:tx1].astype(float)
    txt = cv2.dilate((reg.mean(axis=2) < 200).astype(np.uint8), np.ones((9, 9), np.uint8)) == 0
    yy, xx = np.mgrid[0:reg.shape[0], 0:reg.shape[1]] / 100.0
    A = np.stack([np.ones_like(xx), xx, yy, xx * xx, yy * yy, xx * yy], -1)
    fill = np.zeros_like(reg)
    for ch in range(3):
        cf, *_ = np.linalg.lstsq(A[txt], reg[..., ch][txt], rcond=None)
        fill[..., ch] = A @ cf
    noise = np.random.default_rng(3).normal(0, 1.2, fill.shape[:2])[..., None]
    new = np.clip((fill + noise)[12:-12, 10:], 0, 255).astype(np.uint8)
    use = cv2.dilate((a[ty0:ty1, tx0:tx1].mean(axis=2) < 215).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    use[:1062 - ty0, :588 - tx0] = False          # keep the dad's head outline
    a[ty0:ty1, tx0:tx1][use] = new[use]
    # monitor left edge: rebuild from the clean rows above, following its slight slant
    ref = a[976, 925:990].copy()
    for y in range(ty0, 1128):
        sh = int(round((y - 976) * 3 / 85))
        a[y, 925 + sh:990] = ref[:65 - sh]
    m = np.zeros(lum.shape, np.uint8)
    m[1126:1150, 925:990] = (lum[1126:1150, 925:990] < 140)
    cv2.circle(m, (1099, 1484), 46, 1, -1)
    return cv2.inpaint(a, cv2.dilate(m, np.ones((5, 5), np.uint8)) * 255, 6, cv2.INPAINT_TELEA)


def fit(s, maxw, px0):
    px = px0
    while ImageFont.truetype(FONT, px).getlength(s) > maxw:
        px -= 1
    return px


def text(d, lines, x, y, px, lh, anchor="ma"):
    f = ImageFont.truetype(FONT, px)
    for i, s in enumerate(lines):
        d.text((x, y + i * lh), s, font=f, fill=(12, 12, 12), anchor=anchor)


def post():
    a = np.asarray(Image.open(g.SRC + "fotos/meme_nike.jpg").convert("RGB")).copy()
    a = clean(a)
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    px = fit("mejor que Adidas", 440, 80)
    text(d, ["Papá, Nike es", "mejor que Adidas"], 905, 52, px, int(px * 1.13))
    px2 = fit("escuincle traidor", 345, 80)
    text(d, ["escuincle traidor", "jajajajamuérete"], 742, 992, px2, int(px2 * 1.2))
    im = im.crop((6, 0, 1172, round(1166 * 1.25)))       # drop black side borders, 4:5
    c = im.resize((1080, 1350), Image.LANCZOS).convert("RGBA")
    put(c, badge(110), 82, 82)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    post().convert("RGB").save(OUT + "post-meme-nike.jpg", quality=94, subsampling=0)
    print("ok")
