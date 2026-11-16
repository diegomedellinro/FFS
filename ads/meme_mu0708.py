"""Post meme 'Mira lo que te compré amor' versión Man United 07/08 (1080x1350), adaptado a la marca.
Se quitan los íconos de Instagram (contador y silencio) y se agrega franja con subtítulo, logo y CTA.
Uso: python3 meme_mu0708.py
"""
import os
import numpy as np
from PIL import Image
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from meme_amor import caption
from buenfin_2da50 import pill, GREY, WHITE

SRC = g.SRC + "fotos/meme_mu0708.jpg"
OUT = g.HERE + "out/meme_mu0708/"
W, H = 1080, 1350


def clean():
    """Crop away the Instagram counter (top right) and mute button (bottom right) instead of painting over them."""
    im = Image.open(SRC).convert("RGB").crop((0, 128, 1052, 1159))
    return im.resize((W, round(im.height * W / im.width)), Image.LANCZOS).convert("RGBA")


def build():
    c = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    im = clean()
    c.alpha_composite(im, (0, 0))
    top = im.height
    # fade the art into the black band
    y = np.linspace(0, 1, 120)[:, None]
    fade = Image.fromarray(np.repeat((y * 255).astype(np.uint8), W, 1))
    c.alpha_composite(Image.composite(Image.new("RGBA", (W, 120), (8, 8, 10, 255)), Image.new("RGBA", (W, 120), (0, 0, 0, 0)), fade), (0, top - 120))
    put(c, caption("-MIRA LO QUE TE COMPRÉ AMOR", 56), W / 2, top + 10)
    put(c, text("Man United 07/08 manga larga · Final de Moscú", "MontB.ttf", 28, GREY, 0.03), W / 2, top + 95)
    put(c, pill("3 POR $1,600 · FOOTBALLFRENZY.SHOP", 40), W / 2, top + 175)
    put(c, badge(110), 90, 90)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "post-meme-mu0708.jpg", quality=94, subsampling=0)
    print("ok")
