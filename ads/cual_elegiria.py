"""'Si me conoces bien, ¿cuál elegiría? 😍': cuadrícula 3x3 numerada de jerseys de la tienda sobre negro.

Post 1080x1350 e historia 1080x1920. Solo usa recortes reales de la tienda; el logo va abajo al centro.
Uso: python3 cual_elegiria.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import generar_ads as g
from generar_ads import put
from hf_ads import badge
from chat_doctor import emoji

OUT = g.HERE + "out/elegiria/"
POP = g.HERE + "fonts/Poppins-Bold.ttf"
INK = (17, 17, 17)
NINE = [
    "rm_1112_home.png", "fcb_0809_home.png", "kaka.png",
    "juve.png", "zidane98.png", "arg06.png",
    "viejo/ame1213.png", "cl_fcb_1415.png", "rm1718.png",
]


def pop(s, px, fill):
    f = ImageFont.truetype(POP, px)
    bb = f.getbbox(s)
    im = Image.new("RGBA", (bb[2] - bb[0] + 10, bb[3] - bb[1] + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((5 - bb[0], 5 - bb[1]), s, font=f, fill=fill)
    return im


def header(c, x0, y0, x1, y1, px):
    ImageDraw.Draw(c).rectangle([x0, y0, x1, y1], fill=(244, 244, 244))
    cx, h = (x0 + x1) / 2, y1 - y0
    l1, l2 = pop("Si me conoces bien,", px, INK), pop("¿cuál elegiría?", px, INK)
    e = emoji("😍", int(px * 1.05))
    put(c, l1, cx, y0 + h * 0.30)
    w2 = l2.width + 14 + e.width
    c.alpha_composite(l2, (int(cx - w2 / 2), int(y0 + h * 0.72 - l2.height / 2)))
    c.alpha_composite(e, (int(cx - w2 / 2 + l2.width + 14), int(y0 + h * 0.72 - e.height / 2)))


def jersey(name, w, h):
    im = Image.open(g.SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    s = min(w / im.width, h / im.height)
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def grid(c, top, bottom, margin=36, num_px=54):
    cw = (c.width - 2 * margin) / 3
    rh = (bottom - top) / 3
    for i, name in enumerate(NINE):
        col, row = i % 3, i // 3
        cx = margin + cw * (col + 0.5)
        cy = top + rh * (row + 0.5)
        j = jersey(name, cw * 0.84, rh * 0.80)
        # soft white glow so dark kits (Milan, Barça) separate from the black background
        glow = Image.new("L", c.size, 0)
        glow.paste(j.getchannel("A"), (int(cx - j.width / 2), int(cy - j.height / 2 + 8)))
        glow = glow.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.16))
        c.alpha_composite(Image.composite(Image.new("RGBA", c.size, (255, 255, 255, 255)), Image.new("RGBA", c.size, (0, 0, 0, 0)), glow))
        put(c, j, cx + 8, cy + 8)
        n = pop(f"{i + 1}.", num_px, (255, 255, 255))
        c.alpha_composite(n, (int(cx - cw / 2), int(cy - rh / 2 + 4)))


def post():
    c = Image.new("RGBA", (1080, 1350), (0, 0, 0, 255))
    header(c, 60, 0, 1020, 215, 70)
    grid(c, 240, 1235)
    put(c, badge(96), 540, 1290)
    return c


def story():
    c = Image.new("RGBA", (1080, 1920), (0, 0, 0, 255))
    header(c, 60, 150, 1020, 410, 80)
    grid(c, 450, 1690, num_px=60)
    put(c, badge(120), 540, 1770)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    post().convert("RGB").save(OUT + "post-elegiria.jpg", quality=94, subsampling=0)
    story().convert("RGB").save(OUT + "story-elegiria.jpg", quality=94, subsampling=0)
    print("ok")
