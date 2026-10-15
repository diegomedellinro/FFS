from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import random, os

D = "/tmp/claude-0/-home-user-FFS/b1a678c7-3ace-575d-a444-5e3cff216ec4/"
IMG = D + "images/"
F = D + "scratchpad/fonts/"
OUT = "/home/user/FFS/banners/"

# Football Frenzy palette (from the logo): black, white, neon red
RED = (232, 22, 35)
RED_DEEP = (150, 8, 16)
WHITE = (255, 255, 255)
GREY = (205, 205, 210)
BG = (6, 6, 8)

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


def grade(img):
    """Shift the photo's warm gold toward the brand's black/red look."""
    g = img.convert("L").convert("RGB")
    g = Image.blend(img, g, 0.55)
    r, gch, b = g.split()
    r = r.point(lambda v: min(255, int(v * 1.12)))
    gch = gch.point(lambda v: int(v * 0.88))
    b = b.point(lambda v: int(v * 0.90))
    return Image.merge("RGB", (r, gch, b))


def zoom_blur(img, center, strength=0.06, steps=10, rx_k=0.30, ry_k=0.42):
    """Radial motion blur: stacked zoomed copies, faces kept sharp by a centre mask."""
    W, H = img.size
    cx, cy = center
    acc = img.copy().convert("RGB")
    for i in range(1, steps + 1):
        z = 1 + strength * i / steps
        big = img.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox, oy = int(cx * z - cx), int(cy * z - cy)
        acc = Image.blend(acc, big.crop((ox, oy, ox + W, oy + H)), 1 / (i + 1))
    mask = Image.new("L", (W, H), 255)
    md = ImageDraw.Draw(mask)
    rx, ry = W * rx_k, H * ry_k
    md.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(min(W, H) * 0.12))
    return Image.composite(acc, img, mask)


def text_layer(text, fnt, fill, stroke=0, stroke_fill=None, skew=-0.2, shadow=True):
    bb = fnt.getbbox(text, stroke_width=stroke)
    w, h = bb[2] - bb[0] + 80, bb[3] - bb[1] + 40
    pad = int(abs(skew) * h) + 20
    lay = Image.new("RGBA", (w + pad, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((pad // 2 + 20 - bb[0], 20 - bb[1]), text, font=fnt, fill=fill,
                             stroke_width=stroke, stroke_fill=stroke_fill)
    lay = lay.transform(lay.size, Image.AFFINE, (1, skew, -skew * h / 2, 0, 1, 0), Image.BICUBIC)
    if shadow:
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(12)).point(lambda a: int(a * 0.9)))
        base = Image.new("RGBA", (lay.width + 16, lay.height + 16), (0, 0, 0, 0))
        base.alpha_composite(sh, (10, 12))
        base.alpha_composite(lay, (0, 0))
        lay = base
    return lay


def glow(lay, color, radius=22, strength=0.9):
    """Returns (layer, pad): layer is padded so the glow never gets clipped."""
    p = radius * 3
    big = Image.new("RGBA", (lay.width + 2 * p, lay.height + 2 * p), (0, 0, 0, 0))
    big.alpha_composite(lay, (p, p))
    g = Image.new("RGBA", big.size, color + (0,))
    g.putalpha(big.getchannel("A").filter(ImageFilter.GaussianBlur(radius)).point(lambda a: int(a * strength)))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(big)
    return out, p


def speed_lines(canvas, box, n, seed, slope=-0.30, alpha=(70, 200)):
    random.seed(seed)
    x0, y0, x1, y1 = box
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        y = random.randint(y0, y1)
        x = random.randint(x0, x1)
        L = random.randint(120, 520)
        t = random.choice([2, 2, 3, 4, 6])
        c = random.choice([WHITE, RED, RED, GREY]) + (random.randint(*alpha),)
        d.polygon([(x, y), (x + L, y + L * slope), (x + L + t, y + L * slope), (x + t, y)], fill=c)
    canvas.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.7)))


def slash(canvas, pts, color, blur=0):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon(pts, fill=color)
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(lay)


def logo_layer(width):
    lg = logo.copy()
    lg = lg.crop(lg.convert("L").point(lambda v: 255 if v > 25 else 0).getbbox())
    lg = lg.resize((width, round(lg.height * width / lg.width)), Image.LANCZOS)
    out = lg.convert("RGBA")
    out.putalpha(lg.convert("L").point(lambda v: min(255, int(v * 1.6))))
    return out


def badge(text, fnt, fill, txt_fill, padx=30, pady=14, skew=-0.25):
    bb = fnt.getbbox(text)
    w, h = bb[2] - bb[0] + padx * 2, bb[3] - bb[1] + pady * 2
    off = int(abs(skew) * h)
    lay = Image.new("RGBA", (w + off * 2, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(off * 2, 0), (w + off * 2, 0), (w, h), (0, h)], fill=fill)
    d.text((off + padx - bb[0], pady - bb[1]), text, font=fnt, fill=txt_fill)
    return lay


def offers(c, x, y, s, big):
    """3X2 (white) & 5X3 (red) — returns bottom y."""
    anton = lambda px: font("Anton.ttf", int(px * s))
    t32, p1 = glow(text_layer("3X2", anton(big), WHITE), RED, 26, 0.55)
    amp = text_layer("&", anton(int(big * .45)), RED)
    t53, p2 = glow(text_layer("5X3", anton(big), RED, stroke=max(3, int(5 * s)), stroke_fill=WHITE), RED, 26, 0.75)
    c.alpha_composite(t32, (x - p1, y - p1))
    ax = x + t32.width - 2 * p1 - int(60 * s)
    c.alpha_composite(amp, (ax, y + int(big * .42 * s)))
    c.alpha_composite(t53, (ax + amp.width - int(50 * s) - p2, y - p2))
    return y + t32.height - 2 * p1


def build(W, H, layout):
    c = Image.new("RGBA", (W, H), BG + (255,))
    desktop = layout == "desktop"
    s = W / 1920 if desktop else W / 1080
    anton = lambda px: font("Anton.ttf", int(px * s))
    mont = lambda px: font("MontB.ttf", int(px * s))

    # --- photo: more room, brand grade, motion blur ---
    if desktop:
        pw = int(W * 0.74)
        ph = grade(cover(photo, pw, H, 0.30))
        ph = zoom_blur(ph, (int(pw * 0.56), int(H * 0.42)), 0.07, ry_k=0.62)
        mask = Image.new("L", (pw, H), 255)
        md = ImageDraw.Draw(mask)
        fade = int(pw * 0.30)
        for i in range(fade):
            md.line([(i, 0), (i, H)], fill=int(255 * (i / fade) ** 1.4))
        c.paste(ph.convert("RGBA"), (W - pw, 0), mask)
    else:
        phh = int(H * 0.68)
        ph = grade(cover(photo, W, phh, 0.12))
        ph = zoom_blur(ph, (W // 2, int(phh * 0.45)), 0.07)
        mask = Image.new("L", (W, phh), 255)
        md = ImageDraw.Draw(mask)
        fade = int(phh * 0.30)
        for i in range(fade):
            md.line([(0, phh - 1 - i), (W, phh - 1 - i)], fill=int(255 * (i / fade) ** 1.4))
        c.paste(ph.convert("RGBA"), (0, 0), mask)

    # red light wash from the bottom-left corner for brand colour
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wash).ellipse([-W * .25, H * .55, W * .45, H * 1.5], fill=RED_DEEP + (110,))
    c.alpha_composite(wash.filter(ImageFilter.GaussianBlur(120 * s)))

    # --- motion: slashes + speed lines over the image ---
    if desktop:
        slash(c, [(int(W * .41), H), (int(W * .55), 0), (int(W * .575), 0), (int(W * .435), H)], RED + (210,))
        slash(c, [(int(W * .445), H), (int(W * .585), 0), (int(W * .592), 0), (int(W * .452), H)], WHITE + (200,))
        slash(c, [(int(W * .90), H), (int(W * 1.0), H * .55), (int(W * 1.0), H * .60), (int(W * .925), H)], RED + (190,))
        speed_lines(c, (int(W * .30), 60, W - 200, H), 34, 3, slope=-0.36, alpha=(50, 150))
        speed_lines(c, (0, 160, int(W * .32), H - 30), 26, 9)
    else:
        slash(c, [(0, int(H * .605)), (W, int(H * .515)), (W, int(H * .54)), (0, int(H * .63))], RED + (220,))
        slash(c, [(0, int(H * .64)), (W, int(H * .55)), (W, int(H * .557)), (0, int(H * .647))], WHITE + (210,))
        speed_lines(c, (0, 40, W, int(H * .58)), 30, 3, slope=-0.30, alpha=(50, 140))
        speed_lines(c, (0, int(H * .66), W, H - 40), 20, 9)

    # --- copy ---
    if desktop:
        x, y = int(80 * s), int(215 * s)
        big = 210
    else:
        x, y = int(64 * s), int(H * .655)
        big = 175

    kicker = badge("PROMO POR TIEMPO LIMITADO", mont(28 if desktop else 30), RED, WHITE)
    c.alpha_composite(kicker, (x, y))
    y += kicker.height + int(10 * s)

    y = offers(c, x - int(10 * s), y, s, big) - int(4 * s)

    ap = badge("APLICA EN TODAS LAS JERSEYS", anton(50 if desktop else 52), WHITE, BG, padx=34, pady=14)
    c.alpha_composite(ap, (x, y))
    y += ap.height + int(20 * s)

    d = ImageDraw.Draw(c)
    sub_font = mont(25 if desktop else 31)
    parts = ["ENVÍO GRATIS A TODO MÉXICO" if desktop else "ENVÍO GRATIS", "TALLAS S A 4XL"]
    sx = x + int(6 * s)
    for i, part in enumerate(parts):
        if i:
            d.text((sx, y), "  •  ", font=sub_font, fill=RED)
            sx += int(sub_font.getlength("  •  "))
        d.text((sx, y), part, font=sub_font, fill=GREY)
        sx += int(sub_font.getlength(part))

    lg = logo_layer(int(165 * s) if desktop else int(190 * s))
    c.alpha_composite(lg, (int(60 * s), int(28 * s)))

    # vignette
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).rectangle([0, 0, W, H], outline=255, width=int(60 * s))
    v = v.filter(ImageFilter.GaussianBlur(80 * s))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    dark.putalpha(v.point(lambda a: int(a * 0.5)))
    c.alpha_composite(dark)
    return c.convert("RGB")


os.makedirs(OUT, exist_ok=True)
build(1920, 800, "desktop").save(OUT + "portada-3x2-5x3-desktop-1920x800.jpg", quality=90, optimize=True, progressive=True)
build(1080, 1350, "mobile").save(OUT + "portada-3x2-5x3-movil-1080x1350.jpg", quality=90, optimize=True, progressive=True)
print("ok")
