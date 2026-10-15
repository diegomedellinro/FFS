"""4K hero banners: Barça (3X2 & 5X3 ACTIVE) and Ronaldo retro (JERSEYS RETRO 10% OFF CODE: RETRO10).

Photos are upscaled 4x with Real-ESRGAN first (see scratchpad/sr/upscale.py).
The photo never moves; only the text animates (light sheen + a breathing glow/scale on the key line),
and frame 0 already shows every line so the video poster is complete.
Usage: python3 generar_portadas_4k.py [--video]
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import math, os, sys, shutil, subprocess

S = "/tmp/claude-0/-home-user-FFS/b1a678c7-3ace-575d-a444-5e3cff216ec4/scratchpad/"
F = S + "fonts/"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
TMP = S + "frames4k/"

RED = (226, 20, 32)
INK = (12, 12, 14)
WHITE = (255, 255, 255)

BARCA = Image.open(S + "sr/barca_x4.png").convert("RGB")      # 2944x3680
RONALDO = Image.open(S + "sr/ronaldo_x4.png").convert("RGB")  # 2944x1656


def font(name, px):
    return ImageFont.truetype(F + name, int(px))


def avg(img, box):
    return tuple(int(v) for v in img.crop(box).resize((1, 1), Image.BOX).getpixel((0, 0)))


def vgrad(W, H, stops):
    """Vertical gradient through (t, color) stops."""
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / (H - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / (t1 - t0) if t1 > t0 else 0
                d.line([(0, y), (W, y)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)))
                break
    return bg


def feather_mask(w, h, left=0, right=0, top=0, bottom=0):
    """Edge fades multiplied together, so corners fade on both axes (no visible seams)."""
    import numpy as np
    def ramp(n, size):
        r = np.ones(size, dtype=np.float32)
        if n:
            r[:n] = (np.arange(n, dtype=np.float32) / n) ** 1.3
        return r
    x = ramp(left, w) * ramp(right, w)[::-1]
    y = ramp(top, h) * ramp(bottom, h)[::-1]
    return Image.fromarray((np.outer(y, x) * 255).astype("uint8"), "L")


def place(bg, ph, x, y, mask):
    bg.paste(ph, (x, y), mask)
    return bg


# ---------- text rendering ----------

class Line:
    """One line of text drawn once on its own transparent layer (so it can glow/scale per frame)."""
    def __init__(self, parts, fnt, pad=None):
        self.parts, self.font = parts, fnt
        bb = [fnt.getbbox(t) for t, _ in parts]
        self.asc = min(b[1] for b in bb)
        self.h = max(b[3] for b in bb) - self.asc
        self.w = int(sum(fnt.getlength(t) for t, _ in parts))
        p = pad if pad is not None else int(self.h * 0.6)
        self.pad = p
        self.img = Image.new("RGBA", (self.w + 2 * p, self.h + 2 * p), (0, 0, 0, 0))
        d = ImageDraw.Draw(self.img)
        x = p
        for t, col in parts:
            d.text((x, p - self.asc), t, font=fnt, fill=col)
            x += fnt.getlength(t)


def shadow(layer, blur, alpha, offset):
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda a: int(a * alpha)))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, offset)
    out.alpha_composite(layer)
    return out


def glow(layer, color, blur, k):
    if k <= 0.01:
        return layer
    g = Image.new("RGBA", layer.size, color + (0,))
    g.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda a: int(a * k)))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def sheen(layer, phase, width_k=0.10, strength=170):
    """Soft diagonal highlight sweeping across the glyphs; phase in [0,1] or None."""
    if phase is None:
        return layer
    W, H = layer.size
    cx = -W * 0.2 + phase * W * 1.4
    hw = W * width_k / 2
    band = Image.new("L", (W, H), 0)
    ImageDraw.Draw(band).polygon([(cx - hw, H), (cx + hw, H), (cx + hw + H * .35, 0), (cx - hw + H * .35, 0)], fill=strength)
    band = band.filter(ImageFilter.GaussianBlur(hw * 0.5))
    band = ImageChops.multiply(band, layer.getchannel("A"))
    w = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    w.putalpha(band)
    out = layer.copy()
    out.alpha_composite(w)
    return out


def scaled(layer, s):
    if abs(s - 1) < 1e-3:
        return layer
    W, H = layer.size
    big = layer.resize((round(W * s), round(H * s)), Image.BICUBIC)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(big, ((W - big.width) // 2, (H - big.height) // 2)) if s < 1 else None
    if s >= 1:
        x, y = (big.width - W) // 2, (big.height - H) // 2
        out = big.crop((x, y, x + W, y + H))
    return out


def pill(text, fnt, fill, txt, padx, pady, outline=None, ow=0):
    bb = fnt.getbbox(text)
    w, h = bb[2] - bb[0] + 2 * padx, bb[3] - bb[1] + 2 * pady
    p = int(h * 0.6)
    img = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([p, p, p + w, p + h], radius=h // 2, fill=fill, outline=outline, width=ow)
    d.text((p + padx - bb[0], p + pady - bb[1]), text, font=fnt, fill=txt)
    img.pad, img.w, img.h = p, w, h
    return img


# ---------- banners ----------

class Banner:
    def frame(self, t):
        """t in [0,1) across the loop. t=None -> static poster."""
        c = self.plate.copy().convert("RGBA")
        for item in self.items:
            lay = item["img"]
            if t is not None:
                ph = item.get("sheen")
                if ph:
                    a, b = ph
                    u = (t * 2) % 1
                    lay = sheen(lay, (u - a) / (b - a) if a <= u <= b else None)
                if item.get("pulse"):
                    k = 0.5 - 0.5 * math.cos(2 * math.pi * t * 2)
                    lay = glow(lay, item["pulse"], item["blur"], 0.85 * k)
                    lay = scaled(lay, 1 + 0.035 * k)
            elif item.get("pulse"):
                lay = glow(lay, item["pulse"], item["blur"], 0.35)
            x, y = item["xy"]
            c.alpha_composite(lay, (x - item["pad"], y - item["pad"]))
        return c.convert("RGB")


class Barca(Banner):
    def __init__(self, layout):
        if layout == "desktop":
            W, H = 3840, 1372
            ph = BARCA.resize((round(BARCA.width * H / BARCA.height), H), Image.LANCZOS)
            px = 2040
            bg = vgrad(W, H, [(0, avg(BARCA, (0, 0, 2944, 200))), (.55, avg(BARCA, (0, 1600, 200, 2000))), (1, avg(BARCA, (0, 3480, 2944, 3680)))])
            place(bg, ph, px, 0, feather_mask(ph.width, H, left=int(ph.width * .16), right=int(ph.width * .16)))
            s = H / 1372
            big = Line([("3X2 ", INK), ("& ", RED), ("5X3", RED)], font("Anton.ttf", 330 * s))
            act = pill("ACTIVE", font("Anton.ttf", 120 * s), RED, WHITE, int(70 * s), int(26 * s))
            block_h = big.h + int(60 * s) + act.h
            x0 = int(330 * s)
            y0 = (H - block_h) // 2
            ax = x0 + (big.w - act.w) // 2
            self.items = [
                {"img": shadow(big.img, 18 * s, .25, (0, int(10 * s))), "pad": big.pad, "xy": (x0, y0), "sheen": (0, .45)},
                {"img": act, "pad": act.pad, "xy": (ax, y0 + big.h + int(60 * s)), "pulse": RED, "blur": 40 * s},
            ]
        else:
            W, H = 2160, 2700
            ph_h = 1900
            ph = BARCA.resize((round(BARCA.width * ph_h / BARCA.height), ph_h), Image.LANCZOS)
            px = (W - ph.width) // 2
            floor = avg(BARCA, (0, 3380, 2944, 3680))
            bg = vgrad(W, H, [(0, avg(BARCA, (0, 0, 2944, 200))), (.45, avg(BARCA, (0, 1600, 200, 2000))), (ph_h / H, floor), (1, floor)])
            place(bg, ph, px, 0, feather_mask(ph.width, ph_h, left=int(ph.width * .14), right=int(ph.width * .14), bottom=int(ph_h * .22)))
            s = W / 2160
            big = Line([("3X2 ", INK), ("& ", RED), ("5X3", RED)], font("Anton.ttf", 300 * s))
            act = pill("ACTIVE", font("Anton.ttf", 110 * s), RED, WHITE, int(64 * s), int(24 * s))
            gap = int(50 * s)
            # leave the bottom ~16% free for the theme's "Shop now" button
            y_end = int(H * 0.82)
            y0 = y_end - (big.h + gap + act.h)
            self.items = [
                {"img": shadow(big.img, 16 * s, .25, (0, int(9 * s))), "pad": big.pad, "xy": ((W - big.w) // 2, y0), "sheen": (0, .45)},
                {"img": act, "pad": act.pad, "xy": ((W - act.w) // 2, y0 + big.h + gap), "pulse": RED, "blur": 36 * s},
            ]
        self.W, self.H, self.plate = W, H, bg


class Ronaldo(Banner):
    def __init__(self, layout):
        dark = tuple(int(v * .9) for v in avg(RONALDO, (2400, 0, 2944, 1656)))
        if layout == "desktop":
            W, H = 3840, 1372
            ph = RONALDO.resize((round(RONALDO.width * H / RONALDO.height), H), Image.LANCZOS)  # ~2440 wide
            bg = Image.new("RGB", (W, H), dark)
            pool = Image.new("L", (W, H), 0)
            ImageDraw.Draw(pool).ellipse([W * .5, -H * .3, W * 1.15, H * .95], fill=60)
            bg = Image.composite(Image.new("RGB", (W, H), (60, 8, 12)), bg, pool.filter(ImageFilter.GaussianBlur(W * .08)))
            place(bg, ph, 0, 0, feather_mask(ph.width, H, right=int(ph.width * .35)))
            s = H / 1372
            x0 = int(2250 * s)
            title = Line([("JERSEYS RETRO", WHITE)], font("Anton.ttf", 150 * s))
            big = Line([("10% OFF", RED)], font("Anton.ttf", 330 * s))
            code = pill("CODE: RETRO10", font("Anton.ttf", 92 * s), (0, 0, 0, 0), WHITE, int(56 * s), int(22 * s), outline=WHITE, ow=max(4, int(5 * s)))
            g1, g2 = int(14 * s), int(54 * s)
            block = title.h + g1 + big.h + g2 + code.h
            y0 = (H - block) // 2
            self.items = [
                {"img": shadow(title.img, 18 * s, .6, (0, int(8 * s))), "pad": title.pad, "xy": (x0, y0)},
                {"img": shadow(big.img, 22 * s, .6, (0, int(10 * s))), "pad": big.pad, "xy": (x0, y0 + title.h + g1), "sheen": (0, .45)},
                {"img": code, "pad": code.pad, "xy": (x0, y0 + title.h + g1 + big.h + g2), "pulse": RED, "blur": 34 * s},
            ]
        else:
            W, H = 2160, 2700
            crop = RONALDO.crop((0, 0, 2400, 1656))
            ph = crop.resize((W, round(crop.height * W / crop.width)), Image.LANCZOS)  # 2160 x ~1490
            bg = Image.new("RGB", (W, H), dark)
            place(bg, ph, 0, 0, feather_mask(W, ph.height, bottom=int(ph.height * .3)))
            s = W / 2160
            title = Line([("JERSEYS RETRO", WHITE)], font("Anton.ttf", 150 * s))
            big = Line([("10% OFF", RED)], font("Anton.ttf", 320 * s))
            code = pill("CODE: RETRO10", font("Anton.ttf", 92 * s), (0, 0, 0, 0), WHITE, int(56 * s), int(22 * s), outline=WHITE, ow=max(4, int(5 * s)))
            g1, g2 = int(14 * s), int(50 * s)
            block = title.h + g1 + big.h + g2 + code.h
            y_end = int(H * 0.82)
            y0 = y_end - block
            self.items = [
                {"img": shadow(title.img, 16 * s, .6, (0, int(7 * s))), "pad": title.pad, "xy": ((W - title.w) // 2, y0)},
                {"img": shadow(big.img, 20 * s, .6, (0, int(9 * s))), "pad": big.pad, "xy": ((W - big.w) // 2, y0 + title.h + g1), "sheen": (0, .45)},
                {"img": code, "pad": code.pad, "xy": ((W - code.w) // 2, y0 + title.h + g1 + big.h + g2), "pulse": RED, "blur": 32 * s},
            ]
        self.W, self.H, self.plate = W, H, bg


def render_video(b, path, seconds=8, fps=30):
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    n = seconds * fps
    for i in range(n):
        b.frame(i / n).save(TMP + f"f{i:04d}.png", compress_level=1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", TMP + "f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
                    "-profile:v", "high", "-level", "5.1", "-movflags", "+faststart", "-an", path], check=True)
    shutil.rmtree(TMP)


if __name__ == "__main__":
    video = "--video" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    jobs = [("barca", "desktop", Barca), ("barca", "movil", Barca), ("retro", "desktop", Ronaldo), ("retro", "movil", Ronaldo)]
    for name, lay, cls in jobs:
        if only and f"{name}-{lay}" not in only:
            continue
        b = cls("desktop" if lay == "desktop" else "mobile")
        stem = f"portada-{name}-4k-{lay}-{b.W}x{b.H}"
        b.frame(t=0).save(OUT + stem + ".jpg", quality=95, optimize=True, progressive=True)
        if video:
            render_video(b, OUT + stem + ".mp4")
        print("ok", stem)
