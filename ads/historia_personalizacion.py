"""Historia (1080x1920) con la foto real de jerseys del Real Madrid: 'PERSONALIZACIÓN Y ENVÍO GRATIS'.

Fondo = la misma foto desenfocada y oscurecida; la foto nítida va al centro con esquinas redondeadas y sombra.
Uso: python3 historia_personalizacion.py
"""
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import generar_ads as g
from generar_ads import put, text, RED
from hf_ads import badge

PHOTO = g.HERE + "src/fotos/rm_flatlay.jpg"
OUT = g.HERE + "out/personalizacion/"
W, H = 1080, 1920
WHITE = (255, 255, 255)


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def framed(im, w, r=30):
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=r, fill=255)
    im.putalpha(m)
    p = 50
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(m, (p, p + 18))
    a = a.filter(ImageFilter.GaussianBlur(24)).point(lambda v: int(v * 0.6))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out


def red_pill(s, px):
    t = text(s, "Anton.ttf", px, WHITE, 0.02)
    box = Image.new("RGBA", (t.width + 60, t.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([0, 0, box.width - 1, box.height - 1], radius=18, fill=RED)
    box.alpha_composite(t, (30, 10))
    return box


def build():
    src = Image.open(PHOTO).convert("RGB")
    bg = cover(src, W, H).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.42).convert("RGBA")
    put(bg, text("PERSONALIZACIÓN", "Anton.ttf", 132, WHITE, 0.01), W / 2, 232)
    put(bg, red_pill("Y ENVÍO GRATIS", 92), W / 2, 405)
    put(bg, framed(src, 920), W / 2, 1075)
    put(bg, text("TU NOMBRE Y NÚMERO EN CUALQUIER JERSEY", "MontB.ttf", 30, WHITE, 0.06), W / 2, 1715)
    url = text("FOOTBALLFRENZY.SHOP", "MontB.ttf", 34, WHITE, 0.08)
    logo = badge(110)
    x = (W - (logo.width + 10 + url.width)) // 2
    bg.alpha_composite(logo, (x, 1815 - logo.height // 2))
    bg.alpha_composite(url, (x + logo.width + 10, 1815 - url.height // 2))
    return bg


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "story-personalizacion.jpg", quality=94, subsampling=0)
    print("ok")
