"""Retro 10% OFF hero (desktop 1920x686, mobile 1080x1350) — static JPG + looping MP4.

Dark stadium photo, brand palette, motion = slow push-in on the photo,
light sheen across "10% OFF" and a breathing glow on the code.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import math, os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("base", os.path.join(HERE, "generar_portada_barca.py"))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

D, OUT = base.D, base.OUT
RED, WHITE, GREY = (232, 22, 35), (255, 255, 255), (200, 200, 205)
CODE = "RETRO10"

photo = Image.open(D + "images/17.jpg").convert("RGB")
font, logo_tile = base.font, base.logo_tile
spaced_len, draw_spaced = base.spaced_len, base.draw_spaced


def dark_plate(W, H, ph, x, y, fade_r=0.0, fade_b=0.0):
    """Very dark backdrop sampled from the photo's own bokeh, photo feathered into it."""
    bg_col = tuple(int(c * 0.9) for c in photo.crop((600, 0, 736, 414)).resize((1, 1), Image.BOX).getpixel((0, 0)))
    bg = Image.new("RGB", (W, H), bg_col)
    # soft reddish stadium glow so the empty side isn't flat
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.45, -H * 0.3, W * 1.2, H * 0.9], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.08))
    bg = Image.composite(Image.new("RGB", (W, H), (60, 8, 12)), bg, glow)
    w, h = ph.size
    m = Image.new("L", (w, h), 255)
    md = ImageDraw.Draw(m)
    if fade_r:
        fr = int(w * fade_r)
        for i in range(fr):
            md.line([(w - 1 - i, 0), (w - 1 - i, h)], fill=int(255 * (i / fr) ** 1.3))
    if fade_b:
        fb = int(h * fade_b)
        for i in range(fb):
            v = int(255 * (i / fb) ** 1.3)
            md.line([(0, h - 1 - i), (w, h - 1 - i)], fill=v)
    bg.paste(ph, (x, y), ImageChops.darker(m, Image.new("L", (w, h), 255)))
    return bg


def upscale(img, w, h):
    im = img.resize((w, h), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(1.4, 70, 2))


def copy_block(s, align="left"):
    """JERSEYS RETRO / 10% OFF / code pill / trust line. Returns (layer, boxes)."""
    k_f = font("MontB.ttf", 24 * s)
    t_f = font("Anton.ttf", 78 * s)
    big_f = font("Anton.ttf", 168 * s)
    code_lbl_f = font("MontB.ttf", 22 * s)
    code_f = font("Anton.ttf", 46 * s)
    tr_f = font("MontB.ttf", 19 * s)
    sp = 4 * s

    kick = "SOLO POR TIEMPO LIMITADO"
    title = "JERSEYS RETRO"
    big = "10% OFF"
    lbl = "USA EL CÓDIGO"
    trust = ["ENVÍOS GRATIS", "STOCK LIMITADO", "3,000+ PEDIDOS COMPLETADOS"]
    sep = "   •   "

    pill_pad_x, pill_pad_y = 26 * s, 12 * s
    cb = code_f.getbbox(CODE)
    code_w = cb[2] - cb[0]
    lbl_w = code_lbl_f.getlength(lbl)
    pill_w = lbl_w + 18 * s + code_w + 2 * pill_pad_x
    pill_h = (cb[3] - cb[1]) + 2 * pill_pad_y
    trust_w = sum(tr_f.getlength(t) for t in trust) + tr_f.getlength(sep) * (len(trust) - 1)
    widths = [spaced_len(kick, k_f, sp), t_f.getlength(title), big_f.getlength(big), pill_w, trust_w]
    W = int(max(widths) + 60 * s)
    H = int(560 * s)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    xf = (lambda w: (W - w) / 2) if align == "center" else (lambda w: 0)

    y = 0
    draw_spaced(d, (xf(widths[0]), y), kick, k_f, RED, sp)
    y += 44 * s
    tb = t_f.getbbox(title)
    d.text((xf(widths[1]), y - tb[1]), title, font=t_f, fill=WHITE)
    y += (tb[3] - tb[1]) + 10 * s
    bb = big_f.getbbox(big)
    bx = xf(widths[2])
    d.text((bx, y - bb[1]), big, font=big_f, fill=RED)
    big_box = (int(bx), int(y), int(bx + widths[2]), int(y + bb[3] - bb[1]))
    y += (bb[3] - bb[1]) + 28 * s
    px = xf(pill_w)
    d.rounded_rectangle([px, y, px + pill_w, y + pill_h], radius=int(pill_h / 2), outline=WHITE, width=max(2, int(2.5 * s)))
    lb = code_lbl_f.getbbox(lbl)
    d.text((px + pill_pad_x, y + pill_h / 2 - (lb[1] + lb[3]) / 2), lbl, font=code_lbl_f, fill=GREY)
    cx = px + pill_pad_x + lbl_w + 18 * s
    d.text((cx - cb[0], y + pill_h / 2 - (cb[1] + cb[3]) / 2), CODE, font=code_f, fill=WHITE)
    pill_box = (int(px), int(y), int(px + pill_w), int(y + pill_h))
    y += pill_h + 30 * s
    tx = xf(trust_w)
    for i, t in enumerate(trust):
        if i:
            d.text((tx, y), sep, font=tr_f, fill=RED)
            tx += tr_f.getlength(sep)
        d.text((tx, y), t, font=tr_f, fill=GREY)
        tx += tr_f.getlength(t)
    y += 28 * s
    return lay.crop((0, 0, W, int(y))), big_box, pill_box


def pill_glow(layer, box, k):
    if k <= 0:
        return layer
    x0, y0, x1, y1 = box
    p = 40
    m = Image.new("L", layer.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) // 2, outline=255, width=6)
    m = m.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.9 * k))
    g = Image.new("RGBA", layer.size, RED + (0,))
    g.putalpha(m)
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def pad(layer, p):
    big = Image.new("RGBA", (layer.width + 2 * p, layer.height + 2 * p), (0, 0, 0, 0))
    big.alpha_composite(layer, (p, p))
    return big


class Banner:
    def __init__(self, layout):
        self.layout = layout
        if layout == "desktop":
            self.W, self.H = 1920, 686
            ph = upscale(photo, round(736 * 686 / 414), 686)  # 1220 x 686
            self.plate = dark_plate(self.W, self.H, ph, 0, 0, fade_r=0.35)
            text, self.big_box, self.pill_box = copy_block(0.82)
            self.logo = logo_tile(110)
            gap = 26
            top = (self.H - text.height - self.logo.height - gap) // 2 - 10
            self.text_xy = (1120, top + self.logo.height + gap)
            self.logo_xy = (1120, top)
            self.focus = (int(0.29 * 1220), 300)
        else:
            self.W, self.H = 1080, 1350
            crop = photo.crop((0, 0, 600, 414))
            ph = upscale(crop, 1080, round(414 * 1080 / 600))  # 1080 x 745
            self.plate = dark_plate(self.W, self.H, ph, 0, 0, fade_b=0.30)
            text, self.big_box, self.pill_box = copy_block(0.95, align="center")
            self.logo = logo_tile(130)
            self.text_xy = ((self.W - text.width) // 2, self.H - text.height - 225)
            self.logo_xy = (self.W - self.logo.width - 40, 40)
            self.focus = (330, 400)
        self.P = 60
        self.text = pad(text, self.P)
        self.big_box = tuple(v + self.P for v in self.big_box) + (0, 0)
        self.pill_box = tuple(v + self.P for v in self.pill_box)

    def frame(self, zoom=1.0, sheen_phase=None, glow_k=0.0):
        W, H = self.W, self.H
        if zoom != 1.0:
            fx, fy = self.focus
            big = self.plate.resize((round(W * zoom), round(H * zoom)), Image.BICUBIC)
            ox, oy = round(fx * zoom - fx), round(fy * zoom - fy)
            c = big.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
        else:
            c = self.plate.convert("RGBA")
        t = pill_glow(self.text, self.pill_box, glow_k)
        t = base.sheen(t, self.big_box, sheen_phase)
        c.alpha_composite(t, (self.text_xy[0] - self.P, self.text_xy[1] - self.P))
        c.alpha_composite(self.logo, self.logo_xy)
        return c.convert("RGB")


if __name__ == "__main__":
    video = "--video" in sys.argv
    for layout, name in [("desktop", "portada-retro-desktop-1920x686"), ("mobile", "portada-retro-movil-1080x1350")]:
        b = Banner(layout)
        b.frame().save(OUT + name + ".jpg", quality=92, optimize=True, progressive=True)
        if video:
            base.render_video(b, OUT + name + ".mp4")
    print("ok")
