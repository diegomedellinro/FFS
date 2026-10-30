"""'Nueva temporada 2026/27': pila de jerseys dobladas (1080x1350), sin IA de pago.

Cada jersey recortada de la tienda se convierte en una "jersey doblada": se toma la franja del pecho (escudo +
patrocinador) sin mangas, se le dan esquinas redondeadas, sombreado de pliegue en los lados y se apilan con sombra.
Uso: python3 pila_2627.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge

SRC = g.HERE + "src/"
OUT = g.HERE + "out/pila/"
W, H = 1080, 1350
BG_TOP, BG_BOT = (236, 222, 212), (224, 206, 194)
WINE = (96, 18, 24)

# (archivo, centro vertical de la franja como fracción del alto: escudo + patrocinador). La de arriba arranca en el cuello.
STACK = [
    ("viejo/rm_away_2627.png", None),
    ("spotify/golf.png", 0.34),
    ("outfit/america.png", 0.30),
    ("outfit/psg.png", 0.30),
    ("outfit/miami.png", 0.27),
]
FW, FH = 640, 230     # folded body size (its top ~60px hides under the shirt above)
TOP_FH = 280          # the top one shows the collar
HIDE = 60


def torso(im):
    """Columns of the torso (no sleeves): alpha extent along a row at 70% height."""
    a = np.asarray(im.getchannel("A"))
    row = np.where(a[int(a.shape[0] * 0.7)] > 128)[0]
    return row.min(), row.max()


def folded(name, cy, fh):
    im = Image.open(SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    t0, t1 = torso(im)
    half = (t1 - t0) * 0.62             # torso plus a bit of the folded sleeves
    cx = (t0 + t1) / 2
    x0, x1 = int(max(0, cx - half)), int(min(im.width, cx + half))
    bh = (x1 - x0) * fh / FW
    vis = (HIDE + fh) / 2 / fh          # centre of the visible part of the band
    top = im.height * 0.09 if cy is None else max(0, cy * im.height - bh * vis)
    band = im.crop((x0, int(top), x1, int(top + bh)))
    # fill transparent gaps (collar opening) with the jersey's own color so it reads as cloth
    rgb = np.asarray(band.convert("RGB"), np.float32)
    al = np.asarray(band.getchannel("A"), np.float32)[..., None] / 255
    mean = (rgb * al).sum((0, 1)) / max(al.sum(), 1)
    rgb = rgb * al + mean * (1 - al) * 0.85
    s = max(FW / band.width, fh / band.height)
    body = Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).resize((round(band.width * s), round(band.height * s)), Image.LANCZOS)
    body = body.crop(((body.width - FW) // 2, 0, (body.width - FW) // 2 + FW, fh))
    # fold shading: darker rolled edges left/right and bottom, soft highlight on top
    arr = np.asarray(body, np.float32)
    xs = np.linspace(-1, 1, FW)[None, :, None]
    ys = np.linspace(0, 1, fh)[:, None, None]
    shade = 1 - 0.28 * np.clip((np.abs(xs) - 0.82) / 0.18, 0, 1) ** 1.5 - 0.22 * np.clip((ys - 0.82) / 0.18, 0, 1) ** 1.5
    shade = shade + 0.06 * np.clip((0.12 - ys) / 0.12, 0, 1)
    body = Image.fromarray((arr * shade).clip(0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (FW, fh), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, FW - 1, fh - 1], radius=46, fill=255)
    body.putalpha(m)
    return body


def background():
    yy = np.linspace(0, 1, H)[:, None, None]
    rgb = np.array(BG_TOP, np.float32) * (1 - yy) + np.array(BG_BOT, np.float32) * yy
    rgb = np.broadcast_to(rgb, (H, W, 3)) + np.random.default_rng(3).normal(0, 1.6, (H, W, 3))
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")


def drop(c, piece, x, y):
    sh = Image.new("L", c.size, 0)
    sh.paste(piece.getchannel("A"), (x, y + 14))
    sh = sh.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.35))
    c.alpha_composite(Image.composite(Image.new("RGBA", c.size, (60, 30, 20, 255)), Image.new("RGBA", c.size, (0, 0, 0, 0)), sh))
    c.alpha_composite(piece, (x, y))


def build():
    c = background()
    x = (W - FW) // 2
    step = FH - HIDE
    pieces = [folded(n, cy, TOP_FH if i == 0 else FH) for i, (n, cy) in enumerate(STACK)]
    # bottom of the stack first, top shirt last (drawn on top)
    y_bottom = 1020 - FH
    ys = [y_bottom - (len(pieces) - 1 - i) * step for i in range(len(pieces))]
    ys[0] -= TOP_FH - FH
    for p, y in reversed(list(zip(pieces, ys))):
        drop(c, p, x, y)
    put(c, text("NUEVA TEMPORADA 2026/27", "Anton.ttf", 92, WINE), W / 2, 1105)
    put(c, text("3 POR $1,600  ·  ENVÍO GRATIS", "MontB.ttf", 30, WINE, 0.18), W / 2, 1190)
    put(c, badge(110), W / 2, 1275)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "nueva-temporada-2627.jpg", quality=94, subsampling=0)
    print("ok")
