"""Meme 'chat con el Doctor' (1080x1350) estilo WhatsApp: la receta ilegible resulta ser una jersey de la tienda.

Uso: python3 chat_doctor.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import generar_ads as g
from hf_ads import badge

SRC = g.HERE + "src/"
OUT = g.HERE + "out/doctor/"
W, H = 1080, 1350
INTER = "/usr/share/fonts/opentype/inter/"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
BG = (236, 229, 221)
OUTB, INB = (217, 253, 211), (255, 255, 255)
TICK = (83, 189, 235)
GREY = (102, 119, 129)

JERSEY = "spotify/golf.png"
CAPTION = "La del Barça x Golf. Tómese 3, pague 2"
CAPTION_EMOJI = "💊"


def f(weight, px):
    return ImageFont.truetype(INTER + f"Inter-{weight}.otf", px)


def emoji(ch, px):
    e = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=e, embedded_color=True)
    im = im.crop(im.getchannel("A").getbbox())
    return im.resize((round(im.width * px / im.height), px), Image.LANCZOS)


def wallpaper():
    rng = np.random.default_rng(4)
    a = np.ones((H, W, 3), np.float32) * np.array(BG, np.float32) + rng.normal(0, 1.5, (H, W, 1))
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    # faint doodles like the WhatsApp wallpaper
    for _ in range(70):
        x, y, r = rng.integers(0, W), rng.integers(140, H), rng.integers(10, 26)
        kind = rng.integers(0, 3)
        col = (222, 214, 205, 255)
        if kind == 0:
            d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=3)
        elif kind == 1:
            d.rounded_rectangle([x - r, y - r * 0.7, x + r, y + r * 0.7], radius=6, outline=col, width=3)
        else:
            d.arc([x - r, y - r, x + r, y + r], 200, 340, fill=col, width=3)
    return im


def header(c):
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, W, 132], fill=(246, 246, 246))
    d.line([(0, 132), (W, 132)], fill=(220, 220, 220), width=2)
    d.line([(46, 66), (28, 46)], fill=(20, 20, 20), width=6)
    d.line([(28, 46), (46, 26)], fill=(20, 20, 20), width=6)
    d.text((62, 30), "1.426", font=f("Regular", 40), fill=(20, 20, 20))
    d.ellipse([196, 14, 300, 118], fill=(108, 170, 220))
    c.alpha_composite(emoji("🧑‍⚕️", 78), (210, 26))
    d.text((322, 18), "Doctor", font=f("Bold", 42), fill=(20, 20, 20))
    d.text((322, 70), "en línea", font=f("Regular", 30), fill=GREY)
    # video + phone icons
    d.rounded_rectangle([790, 42, 852, 86], radius=10, outline=(20, 20, 20), width=5)
    d.polygon([(852, 64), (882, 44), (882, 84)], outline=(20, 20, 20), fill=None, width=5)
    # phone handset: thick arc with two ear/mouth pads
    d.arc([918, 30, 1002, 114], 95, 175, fill=(20, 20, 20), width=9)
    d.arc([918, 30, 1002, 114], 185, 265, fill=(20, 20, 20), width=9)
    d.rounded_rectangle([954, 26, 980, 44], radius=7, fill=(20, 20, 20))
    d.rounded_rectangle([914, 64, 932, 90], radius=7, fill=(20, 20, 20))


def day_pill(c, y):
    d = ImageDraw.Draw(c)
    t = "Hoy"
    w = d.textlength(t, font=f("SemiBold", 30)) + 50
    d.rounded_rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 52], radius=18, fill=(255, 255, 255))
    d.text((W / 2, y + 26), t, font=f("SemiBold", 30), fill=(30, 30, 30), anchor="mm")


def ticks(d, x, y):
    for dx in (0, 12):
        d.line([(x + dx, y + 10), (x + dx + 8, y + 18)], fill=TICK, width=4)
        d.line([(x + dx + 8, y + 18), (x + dx + 24, y)], fill=TICK, width=4)


def bubble(c, x0, y0, x1, y1, out=True):
    d = ImageDraw.Draw(c)
    col = OUTB if out else INB
    d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=col)
    if out:
        d.polygon([(x1 - 24, y0), (x1 + 16, y0), (x1, y0 + 26)], fill=col)
    else:
        d.polygon([(x0 + 24, y0), (x0 - 16, y0), (x0, y0 + 26)], fill=col)
    return d


def text_msg(c, y, s, out=True, time="11:30"):
    tf = f("Regular", 38)
    d = ImageDraw.Draw(c)
    tw = d.textlength(s, font=tf)
    w = tw + 70 + (130 if out else 90)
    x1 = W - 40 if out else 40 + w
    x0 = x1 - w
    d = bubble(c, x0, y, x1, y + 100, out)
    d.text((x0 + 34, y + 22), s, font=tf, fill=(17, 27, 33))
    tx = x1 - (128 if out else 90)
    d.text((tx, y + 58), time, font=f("Regular", 26), fill=GREY)
    if out:
        ticks(d, x1 - 52, y + 62)
    return y + 100


def scribble():
    im = Image.new("RGBA", (640, 170), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    pts = []
    sx, sy = 640 / 720, 170 / 220
    for t in np.linspace(0, 1, 400):
        if t < 0.12:     # first loop, like a capital letter
            a = t / 0.12 * 2 * np.pi
            pts.append((120 + 30 * np.sin(a) + 40 * t / 0.12, 120 - 70 * np.sin(a / 2) + 40 * (1 - np.cos(a))))
        elif t < 0.25:
            u = (t - 0.12) / 0.13
            pts.append((160 + 80 * u, 80 + 12 * np.sin(u * 9)))
        else:
            u = (t - 0.25) / 0.75
            pts.append((240 + 380 * u, 82 + 6 * np.sin(u * 3) - 4 * u))
    pts = [(x * sx, y * sy) for x, y in pts]
    d.line(pts, fill=(15, 15, 15), width=6, joint="curve")
    d.arc([600 * sx, 50 * sy, 650 * sx, 90 * sy], 180, 360, fill=(15, 15, 15), width=6)
    d.line([(118 * sx, 120 * sy), (98 * sx, 190 * sy)], fill=(15, 15, 15), width=6)
    return im


def photo_msg(c, y, img, out=True, h=None):
    pw = img.width
    ph = img.height
    x1 = W - 40 if out else 40 + pw + 28
    x0 = x1 - pw - 28
    bh = ph + 28 + (60 if out else 120)
    d = bubble(c, x0, y, x1, y + bh, out)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=22, fill=255)
    c.paste(img.convert("RGB"), (x0 + 14, y + 14), m)
    return x0, x1, y + bh, d


def linen_photo(name, w, h):
    rng = np.random.default_rng(9)
    base = np.ones((h, w, 3), np.float32) * np.array([226, 222, 214], np.float32)
    weave = (np.sin(np.arange(w) * 1.7)[None, :] + np.sin(np.arange(h) * 1.9)[:, None]) * 2.0
    base = base + weave[..., None] + rng.normal(0, 3, (h, w, 1))
    yy = np.linspace(-1, 1, h)[:, None, None]
    xx = np.linspace(-1, 1, w)[None, :, None]
    base = base * (1 - 0.10 * (xx ** 2 + yy ** 2))
    im = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    j = Image.open(SRC + name).convert("RGBA")
    j = j.crop(j.getchannel("A").getbbox())
    s = min(w * 0.98 / j.width, h * 1.05 / j.height)
    j = j.resize((round(j.width * s), round(j.height * s)), Image.LANCZOS).rotate(-3, Image.BICUBIC, expand=True)
    sh = Image.new("L", im.size, 0)
    px, py = (w - j.width) // 2, (h - j.height) // 2 + 30
    sh.paste(j.getchannel("A"), (px + 8, py + 14))
    sh = sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.35))
    im.alpha_composite(Image.composite(Image.new("RGBA", im.size, (40, 35, 30, 255)), Image.new("RGBA", im.size, (0, 0, 0, 0)), sh))
    im.alpha_composite(j, (px, py))
    return im


def build():
    c = wallpaper()
    header(c)
    day_pill(c, 168)
    y = text_msg(c, 250, "Hola Doc, no entiendo lo que me recetó", True, "11:30")
    # outgoing photo of the prescription scribble
    x0, x1, y2, d = photo_msg(c, y + 22, scribble(), True)
    d.text((x1 - 128, y2 - 46), "11:30", font=f("Regular", 26), fill=GREY)
    ticks(d, x1 - 52, y2 - 42)
    # incoming jersey photo with caption
    ph = linen_photo(JERSEY, 760, 400)
    x0, x1, y3, d = photo_msg(c, y2 + 26, ph, False)
    cf = f("Regular", 36)
    d.text((x0 + 26, y3 - 98), CAPTION, font=cf, fill=(17, 27, 33))
    cw = d.textlength(CAPTION, font=cf)
    c.alpha_composite(emoji(CAPTION_EMOJI, 38), (int(x0 + 34 + cw), y3 - 98))
    d.text((x1 - 92, y3 - 46), "11:31", font=f("Regular", 26), fill=GREY)
    text_msg(c, y3 + 24, "¡Gracias Doc!", True, "11:31")
    c.alpha_composite(badge(104), (34, H - 126))
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build().convert("RGB").save(OUT + "chat-doctor.jpg", quality=94, subsampling=0)
    print("ok")
