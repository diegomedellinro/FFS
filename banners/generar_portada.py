from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import random, sys

D = "/tmp/claude-0/-home-user-FFS/b1a678c7-3ace-575d-a444-5e3cff216ec4/"
IMG = D + "images/"
F = D + "scratchpad/fonts/"
OUT = "/home/user/FFS/banners/"
GOLD = (236, 186, 92)
GOLD2 = (255, 214, 130)
RED = (226, 30, 38)
WHITE = (255, 255, 255)
BG = (10, 10, 12)

photo = Image.open(IMG + "14.jpg").convert("RGB")
logo = Image.open(IMG + "15.webp").convert("RGB")


def font(name, size):
    return ImageFont.truetype(F + name, size)


def cover(img, w, h, focus_y=0.45):
    r = max(w / img.width, h / img.height)
    im = img.resize((round(img.width * r), round(img.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = int((im.height - h) * focus_y)
    return im.crop((x, y, x + w, y + h))


def text_layer(size, text, fnt, fill, stroke=0, stroke_fill=None, skew=-0.18, shadow=True):
    """Render text on its own layer, italic-skewed for motion."""
    bb = fnt.getbbox(text, stroke_width=stroke)
    w, h = bb[2] - bb[0] + 80, bb[3] - bb[1] + 40
    pad = int(abs(skew) * h) + 20
    lay = Image.new("RGBA", (w + pad, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((pad // 2 + 20 - bb[0], 20 - bb[1]), text, font=fnt, fill=fill,
           stroke_width=stroke, stroke_fill=stroke_fill)
    lay = lay.transform(lay.size, Image.AFFINE, (1, skew, -skew * h / 2, 0, 1, 0), Image.BICUBIC)
    if shadow:
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda a: int(a * 0.85)))
        base = Image.new("RGBA", (lay.width + 16, lay.height + 16), (0, 0, 0, 0))
        base.alpha_composite(sh, (12, 14))
        base.alpha_composite(lay, (0, 0))
        lay = base
    return lay


def glow(lay, color, radius=22, strength=0.9):
    p = radius * 3
    big = Image.new("RGBA", (lay.width + 2 * p, lay.height + 2 * p), (0, 0, 0, 0))
    big.alpha_composite(lay, (p, p))
    lay = big
    g = Image.new("RGBA", lay.size, color + (0,))
    g.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(radius)).point(lambda a: int(a * strength)))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(lay)
    return out


def streaks(canvas, box, n, colors, seed=7):
    random.seed(seed)
    x0, y0, x1, y1 = box
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        y = random.randint(y0, y1)
        x = random.randint(x0, x1)
        L = random.randint(80, 420)
        t = random.choice([2, 3, 4, 6])
        c = random.choice(colors) + (random.randint(60, 170),)
        d.polygon([(x, y), (x + L, y - L * 0.32), (x + L + t, y - L * 0.32), (x + t, y)], fill=c)
    canvas.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.6)))


def logo_layer(width):
    """Logo has a pure black background: use luminance as alpha so it floats on dark art."""
    lg = logo.copy()
    # crop to content
    bbox = lg.convert("L").point(lambda v: 255 if v > 25 else 0).getbbox()
    lg = lg.crop(bbox)
    r = width / lg.width
    lg = lg.resize((width, round(lg.height * r)), Image.LANCZOS)
    a = lg.convert("L").point(lambda v: min(255, int(v * 1.6)))
    out = lg.convert("RGBA")
    out.putalpha(a)
    return out


def badge(text, fnt, fill, txt_fill, padx=34, pady=16, skew=-0.25):
    bb = fnt.getbbox(text)
    w, h = bb[2] - bb[0] + padx * 2, bb[3] - bb[1] + pady * 2
    off = int(abs(skew) * h)
    lay = Image.new("RGBA", (w + off * 2, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(off * 2, 0), (w + off * 2, 0), (w, h), (0, h)], fill=fill)
    d.text((off + padx - bb[0], pady - bb[1]), text, font=fnt, fill=txt_fill)
    return lay


def build(W, H, layout):
    c = Image.new("RGBA", (W, H), BG + (255,))
    if layout == "desktop":
        pw = int(W * 0.62)
        ph = cover(photo, pw, H, 0.30).convert("RGBA")
        mask = Image.new("L", (pw, H), 255)
        md = ImageDraw.Draw(mask)
        fade = int(pw * 0.42)
        for i in range(fade):
            md.line([(i, 0), (i, H)], fill=int(255 * (i / fade) ** 1.6))
        c.paste(ph, (W - pw, 0), mask)
    else:
        ph = cover(photo, W, int(H * 0.62), 0.15).convert("RGBA")
        mask = Image.new("L", ph.size, 255)
        md = ImageDraw.Draw(mask)
        fade = int(ph.height * 0.45)
        for i in range(fade):
            y = ph.height - 1 - i
            md.line([(0, y), (W, y)], fill=int(255 * (i / fade) ** 1.6))
        c.paste(ph, (0, 0), mask)

    # warm gold light leak + red diagonal accent for energy
    leak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leak)
    if layout == "desktop":
        ld.polygon([(int(W * .30), H), (int(W * .44), 0), (int(W * .47), 0), (int(W * .33), H)], fill=RED + (150,))
        ld.polygon([(int(W * .345), H), (int(W * .485), 0), (int(W * .495), 0), (int(W * .355), H)], fill=GOLD + (170,))
    else:
        ld.polygon([(0, int(H * .60)), (W, int(H * .50)), (W, int(H * .53)), (0, int(H * .63))], fill=RED + (150,))
        ld.polygon([(0, int(H * .645)), (W, int(H * .545)), (W, int(H * .555)), (0, int(H * .655))], fill=GOLD + (170,))
    c.alpha_composite(leak.filter(ImageFilter.GaussianBlur(2)))

    s = W / 1920 if layout == "desktop" else W / 1080
    anton = lambda px: font("Anton.ttf", int(px * s))
    mont = lambda px: font("MontB.ttf", int(px * s))

    if layout == "desktop":
        streaks(c, (0, 120, int(W * .5), H - 40), 38, [GOLD, WHITE, RED])
        x, y = int(90 * s), int(215 * s)
    else:
        streaks(c, (0, int(H * .55), W, H - 60), 30, [GOLD, WHITE, RED])
        x, y = int(70 * s), int(H * 0.585)

    kicker = badge("PROMO POR TIEMPO LIMITADO", mont(30), RED, WHITE)
    c.alpha_composite(kicker, (x, y))
    y += kicker.height + int(18 * s)

    big = 230 if layout == "desktop" else 190
    t32 = glow(text_layer(None, "3X2", anton(big), GOLD2), GOLD, 30, 0.55)
    amp = text_layer(None, "&", anton(int(big * .5)), WHITE)
    t53 = glow(text_layer(None, "5X3", anton(big), RED, stroke=max(3, int(5 * s)), stroke_fill=WHITE), RED, 26, 0.7)
    gx = x - int(20 * s)
    c.alpha_composite(t32, (gx - 90, y - int(10 * s) - 90))
    ax = gx + t32.width - 180 - int(55 * s)
    c.alpha_composite(amp, (ax, y + int(big * .38 * s)))
    c.alpha_composite(t53, (ax + amp.width - int(45 * s) - 78, y - int(10 * s) - 78))
    y += t32.height - 180 - int(10 * s)

    act = badge("ACTIVE ALL JERSEYS", anton(64), WHITE, BG, padx=40, pady=18)
    c.alpha_composite(act, (x, y))
    y += act.height + int(22 * s)

    d = ImageDraw.Draw(c)
    sub = "ENVÍO GRATIS A TODO MÉXICO  •  PERSONALIZA NOMBRE Y NÚMERO" if layout == "desktop" else "ENVÍO GRATIS  •  NOMBRE Y NÚMERO"
    d.text((x + int(6 * s), y), sub, font=mont(26 if layout == "desktop" else 32), fill=(230, 230, 230))

    lg = logo_layer(int(175 * s) if layout == "desktop" else int(200 * s))
    c.alpha_composite(lg, (int(60 * s), int(28 * s)))

    # subtle vignette
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).rectangle([0, 0, W, H], outline=255, width=int(60 * s))
    v = v.filter(ImageFilter.GaussianBlur(80 * s))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    dark.putalpha(v.point(lambda a: int(a * 0.55)))
    c.alpha_composite(dark)
    return c.convert("RGB")


import os
os.makedirs(OUT, exist_ok=True)
build(1920, 800, "desktop").save(OUT + "portada-3x2-5x3-desktop-1920x800.jpg", quality=90, optimize=True, progressive=True)
build(1080, 1350, "mobile").save(OUT + "portada-3x2-5x3-movil-1080x1350.jpg", quality=90, optimize=True, progressive=True)
print("ok")
