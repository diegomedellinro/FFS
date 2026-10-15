"""Hero banners (desktop 1920x800, mobile 1080x1350) — static JPG + looping MP4.

Motion is in the image itself: slow push-in on the photo and a soft light
sheen across the offer, no stripes or lines.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, subprocess, shutil, sys

D = "/tmp/claude-0/-home-user-FFS/b1a678c7-3ace-575d-a444-5e3cff216ec4/"
F = D + "scratchpad/fonts/"
OUT = "/home/user/FFS/banners/"
TMP = D + "scratchpad/frames/"

RED = (226, 20, 32)
INK = (12, 12, 14)
MUTED = (70, 70, 76)

photo = Image.open(D + "scratchpad/barca_clean.png").convert("RGB")
logo_src = Image.open(D + "images/15.webp").convert("RGB")


def font(name, px):
    return ImageFont.truetype(F + name, int(px))


def cover(img, w, h):
    r = max(w / img.width, h / img.height)
    im = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def _avg(img, box):
    c = img.crop(box).resize((1, 1), Image.BOX).getpixel((0, 0))
    return tuple(int(v) for v in c)


def photo_plate(W, H, box, feather_bottom=False):
    """Clean studio backdrop (colours sampled from the photo) + crisp photo feathered into it."""
    top = _avg(photo, (0, 0, photo.width, 60))
    mid = _avg(photo, (0, photo.height // 2 - 40, 60, photo.height // 2 + 40))
    bot = _avg(photo, (0, photo.height - 60, photo.width, photo.height))
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / (H - 1)
        a, b, k = (top, mid, t * 2) if t < 0.5 else (mid, bot, (t - 0.5) * 2)
        d.line([(0, y), (W, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3)))
    # soft light pool behind the players
    x, y, w, h = box
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([x - w * 0.3, y + h * 0.05, x + w * 1.3, y + h * 0.95], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(w * 0.25))
    bg = Image.composite(Image.new("RGB", (W, H), (250, 251, 253)), bg, glow)

    ph = photo.resize((w, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    ex = int(w * 0.16)
    ey = int(h * 0.08) if feather_bottom else 0
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rectangle([ex, -h, w - ex, h - ey if ey else 2 * h], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(ex * 0.45))
    bg.paste(ph, (x, y), m)
    return bg


def logo_tile(size):
    """Logo kept on its own black rounded tile so the white script reads on a light page."""
    lg = logo_src.crop(logo_src.convert("L").point(lambda v: 255 if v > 25 else 0).getbbox())
    pad = int(size * 0.12)
    inner = size - 2 * pad
    lg = lg.resize((inner, round(lg.height * inner / lg.width)), Image.LANCZOS)
    th = lg.height + 2 * pad
    tile = Image.new("RGBA", (size, th), (0, 0, 0, 0))
    m = Image.new("L", (size, th), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, th - 1], radius=int(size * 0.14), fill=255)
    tile.paste((8, 8, 10, 255), (0, 0), m)
    tile.paste(lg, (pad, pad))
    return tile


def draw_spaced(d, xy, text, fnt, fill, spacing):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + spacing
    return x


def spaced_len(text, fnt, spacing):
    return sum(fnt.getlength(ch) + spacing for ch in text) - spacing


def text_block(scale, align="left", max_w=None):
    """Render the copy once on a transparent layer; returns (layer, offer_box)."""
    s = scale
    kick_f = font("MontB.ttf", 22 * s)
    big_f = font("Anton.ttf", 150 * s)
    amp_f = font("Anton.ttf", 84 * s)
    ap_f = font("Anton.ttf", 44 * s)
    sub_f = font("MontB.ttf", 20 * s)

    kick = "PROMO POR TIEMPO LIMITADO"
    sub_parts = ["ENVÍO GRATIS A TODO MÉXICO", "TALLAS S A 4XL"]
    sp = 4 * s

    w32 = big_f.getlength("3X2")
    wamp = amp_f.getlength("&")
    w53 = big_f.getlength("5X3")
    gap = 26 * s
    offer_w = w32 + gap + wamp + gap + w53
    ap = "APLICA EN TODAS LAS JERSEYS"
    widths = [spaced_len(kick, kick_f, sp), offer_w, ap_f.getlength(ap),
              sum(sub_f.getlength(p) for p in sub_parts) + sub_f.getlength("   •   ")]
    W = int(max(widths) + 40 * s)
    H = int(360 * s)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def x_for(w):
        return (W - w) / 2 if align == "center" else 0

    y = 0
    draw_spaced(d, (x_for(widths[0]), y), kick, kick_f, RED, sp)
    y += 40 * s
    ox = x_for(offer_w)
    asc = big_f.getbbox("3X2")
    d.text((ox, y - asc[1]), "3X2", font=big_f, fill=INK)
    ab = amp_f.getbbox("&")
    d.text((ox + w32 + gap, y + (asc[3] - asc[1]) * 0.55 - ab[1] - (ab[3] - ab[1]) / 2), "&", font=amp_f, fill=RED)
    x53 = ox + w32 + gap + wamp + gap
    d.text((x53, y - asc[1]), "5X3", font=big_f, fill=RED)
    offer_box = (int(ox), int(y), int(ox + offer_w), int(y + asc[3] - asc[1]), int(x53), int(x53 + w53))
    y += (asc[3] - asc[1]) + 22 * s
    bb = ap_f.getbbox(ap)
    d.text((x_for(widths[2]), y - bb[1]), ap, font=ap_f, fill=INK)
    y += (bb[3] - bb[1]) + 22 * s
    sx = x_for(widths[3])
    for i, part in enumerate(sub_parts):
        if i:
            d.text((sx, y), "   •   ", font=sub_f, fill=RED)
            sx += sub_f.getlength("   •   ")
        d.text((sx, y), part, font=sub_f, fill=MUTED)
        sx += sub_f.getlength(part)
    y += 30 * s
    return lay.crop((0, 0, W, int(y))), offer_box


def sheen(layer, box, phase):
    """Diagonal soft highlight sweeping across the offer text (masked to the glyphs)."""
    if phase is None:
        return layer
    x0, y0, x1, y1 = box[:4]
    w = x1 - x0
    cx = x0 - w * 0.3 + phase * w * 1.6
    band = Image.new("L", layer.size, 0)
    bd = ImageDraw.Draw(band)
    hw = w * 0.07
    bd.polygon([(cx - hw, y1 + 20), (cx + hw, y1 + 20), (cx + hw + (y1 - y0) * 0.4, y0 - 20), (cx - hw + (y1 - y0) * 0.4, y0 - 20)], fill=170)
    band = band.filter(ImageFilter.GaussianBlur(hw * 0.6))
    a = layer.getchannel("A")
    from PIL import ImageChops
    band = ImageChops.multiply(band, a)
    white = Image.new("RGBA", layer.size, (255, 255, 255, 0))
    white.putalpha(band)
    out = layer.copy()
    out.alpha_composite(white)
    return out


def pulse_53(layer, box, k):
    """Very soft red glow behind 5X3 that breathes with k in [0,1]."""
    if k <= 0:
        return layer
    x0, y0, x1, y1, a0, a1 = box
    m = Image.new("L", layer.size, 0)
    glyph = layer.getchannel("A").crop((a0, y0, a1, y1))
    m.paste(glyph, (a0, y0))
    m = m.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.45 * k))
    g = Image.new("RGBA", layer.size, RED + (0,))
    g.putalpha(m)
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


class Banner:
    def __init__(self, layout):
        self.layout = layout
        if layout == "desktop":
            self.W, self.H = 1920, 800
            ph_h = 800
            ph_w = round(photo.width * ph_h / photo.height)
            self.photo_box = (1020, 0, ph_w, ph_h)
            self.text, self.offer = text_block(1.0)
            self.text_xy = (200, (self.H - self.text.height) // 2 + 40)
            self.logo = logo_tile(150)
            self.logo_xy = (200, self.text_xy[1] - self.logo.height - 36)
            self.focus = (1020 + ph_w // 2, 420)
        else:
            self.W, self.H = 1080, 1350
            ph_h = 1080
            ph_w = round(photo.width * ph_h / photo.height)
            self.photo_box = ((self.W - ph_w) // 2, 0, ph_w, ph_h)
            self.text, self.offer = text_block(0.92, align="center")
            self.text_xy = ((self.W - self.text.width) // 2, self.H - self.text.height - 55)
            self.logo = logo_tile(150)
            self.logo_xy = (40, 40)
            self.focus = (self.W // 2, 520)
        self.plate = photo_plate(self.W, self.H, self.photo_box, feather_bottom=(layout != "desktop"))

    def frame(self, zoom=1.0, sheen_phase=None, glow_k=0.0):
        W, H = self.W, self.H
        if zoom != 1.0:
            fx, fy = self.focus
            big = self.plate.resize((round(W * zoom), round(H * zoom)), Image.BICUBIC)
            ox, oy = round(fx * zoom - fx), round(fy * zoom - fy)
            base = big.crop((ox, oy, ox + W, oy + H))
        else:
            base = self.plate.copy()
        c = base.convert("RGBA")
        t = pulse_53(self.text, self.offer, glow_k)
        t = sheen(t, self.offer, sheen_phase)
        c.alpha_composite(t, self.text_xy)
        c.alpha_composite(self.logo, self.logo_xy)
        return c.convert("RGB")


def ease(x):
    return 0.5 - 0.5 * math.cos(math.pi * x)


def render_video(b, path, seconds=8, fps=30):
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    n = seconds * fps
    for i in range(n):
        t = i / n
        zoom = 1.0 + 0.06 * ease(1 - abs(2 * t - 1))       # push in, ease back: seamless loop
        sp = (t * 2) % 1                                   # sheen sweeps twice per loop
        sweep = sp / 0.35 if sp < 0.35 else None
        glow_k = 0.5 + 0.5 * math.sin(2 * math.pi * t * 2)
        b.frame(zoom, sweep, glow_k).save(TMP + f"f{i:04d}.jpg", quality=92)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", TMP + "f%04d.jpg",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "slow",
                    "-movflags", "+faststart", "-an", path], check=True)
    shutil.rmtree(TMP)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    video = "--video" in sys.argv
    for layout, name in [("desktop", "portada-barca-desktop-1920x800"), ("mobile", "portada-barca-movil-1080x1350")]:
        b = Banner(layout)
        b.frame().save(OUT + name + ".jpg", quality=92, optimize=True, progressive=True)
        if video:
            render_video(b, OUT + name + ".mp4")
    print("ok")
