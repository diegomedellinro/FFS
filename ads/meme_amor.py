"""Meme 'Mira lo que te compré amor' (post 1080x1350) con la marca: se recorta la interfaz de Instagram,
se borra el subtítulo original (inpainting) y se rotula de nuevo con logo y CTA.
Uso: python3 meme_amor.py
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import generar_ads as g
from generar_ads import put
from hf_ads import badge

SRC = g.HERE + "src/fotos/meme_amor.jpg"
OUT = g.HERE + "out/meme_amor/"
W, H = 1080, 1350
YELLOW = (247, 200, 46)
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"


def clean():
    a = cv2.imread(SRC)
    # subtitle: yellow letters + their dark outline, only in the caption band
    y0, y1 = 1195, 1300
    band = a[y0:y1]
    b, g_, r = band[..., 0].astype(int), band[..., 1].astype(int), band[..., 2].astype(int)
    yellow = (r > 170) & (g_ > 130) & (b < 120)
    m = np.zeros(a.shape[:2], np.uint8)
    m[y0:y1] = yellow.astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((9, 9), np.uint8))
    a = cv2.inpaint(a, m, 7, cv2.INPAINT_TELEA)
    # crop away the Instagram UI on the right (counter, like/comment/share icons)
    x1 = 1035
    h = round(x1 * H / W)
    top = 140
    a = a[top:top + h, :x1]
    return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB)).resize((W, H), Image.LANCZOS).convert("RGBA")


def caption(s, px, fill=YELLOW, stroke=6):
    f = ImageFont.truetype(FONT, px)
    bb = f.getbbox(s, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))
    return im


def build():
    c = clean()
    # soft dark band at the bottom: hides inpainting leftovers and makes the caption read like a subtitle
    y = np.linspace(0, 1, H)[:, None]
    a = (np.clip((y - 0.78) / 0.12, 0, 1) * 0.62 * 255).astype(np.uint8)
    shade = Image.new("RGBA", (W, H), (8, 8, 20, 255))
    shade.putalpha(Image.fromarray(np.repeat(a, W, 1)))
    c.alpha_composite(shade)
    put(c, caption("-MIRA LO QUE TE COMPRÉ AMOR", 54), W / 2, 1155)
    put(c, caption("3X2 EN TODAS LAS JERSEYS · FOOTBALLFRENZY.SHOP", 28, (255, 255, 255), 4), W / 2, 1255)
    put(c, badge(110), 95, 95)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "post-meme-amor.jpg", quality=94, subsampling=0)
    print("ok")
