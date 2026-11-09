"""Video 'Buen Fin en vivo' (1080x1350, ~13 s, 30 fps): formato transmisión de partido.

Marcador arriba (FFS 0×0 · EN VIVO) que va metiendo goles: 1×0 = 3x2, 2×0 = 5x3, FINAL = CTA.
Fondo azul estadio con reflectores, texto crema/dorado, cintillo inferior tipo TV, confeti en cada gol.
Uso: python3 video_buenfin_partido.py  →  out/video_buenfin/buen-fin-partido.mp4
"""
import math
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text, ease, back
from hf_ads import badge

OUT = g.HERE + "out/video_buenfin/"
W, H, FPS, DUR = 1080, 1350, 30, 13.0
NAVY, NAVY2 = (14, 26, 58), (6, 12, 30)
CREAM, GOLD, RED, WHITE = (246, 236, 214), (226, 190, 110), (220, 32, 44), (255, 255, 255)
ANTON = "Anton.ttf"
G1, G2, G3 = 3.0, 6.6, 10.0          # goal 1, goal 2, full time


def stadium():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / H
    img = np.array(NAVY, np.float32) * (1 - t[..., None]) + np.array(NAVY2, np.float32) * t[..., None]
    for cx in (0.18, 0.5, 0.82):           # spotlight cones from the top
        w = 0.10 + 0.55 * (yy / H)
        d = np.abs(xx / W - cx) / w
        a = np.clip(1 - d, 0, 1) ** 2 * (1 - yy / H) ** 1.4 * 0.33
        img = img + a[..., None] * 255 * np.array([0.55, 0.65, 0.95])
    v = np.sqrt(((xx / W - 0.5) * 1.2) ** 2 + ((yy / H - 0.5) * 1.0) ** 2)
    img = img * (1 - 0.55 * np.clip(v - 0.25, 0, 1)[..., None])
    img = img + np.random.default_rng(1).normal(0, 2.5, (H, W, 1))
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")


def gold_text(s, px, track=0.0):
    lay = text(s, ANTON, px, WHITE, track)
    h = lay.height
    t = np.linspace(0, 1, h)[:, None, None]
    top, bot = np.array((248, 222, 160), np.float32), np.array((196, 150, 70), np.float32)
    rgb = (top * (1 - t) + bot * t)
    rgb = np.broadcast_to(rgb, (h, lay.width, 3)).astype(np.uint8)
    out = Image.fromarray(rgb).convert("RGBA")
    out.putalpha(lay.getchannel("A"))
    return shadow(out)


def shadow(lay, k=0.55, r=10):
    p = r * 3
    out = Image.new("RGBA", (lay.width + 2 * p, lay.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(lay.getchannel("A"), (p, p + r // 2))
    a = a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * k))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 10, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(lay, (p, p))
    return out


def cream(s, px, track=0.0):
    return shadow(text(s, ANTON, px, CREAM, track))


def box(lay, fill, padx=22, pady=10):
    b = Image.new("RGBA", (lay.width + 2 * padx, lay.height + 2 * pady), fill + (255,))
    b.alpha_composite(lay, (padx, pady))
    return b


def scoreboard(score, live=True):
    h = 74
    logo = badge(58)
    name = text("FFS", ANTON, 38, WHITE, 0.04)
    sc = text(score, ANTON, 40, NAVY2, 0.04)
    parts = []
    seg1 = Image.new("RGBA", (logo.width + name.width + 20, h), (10, 22, 60, 255))
    seg1.alpha_composite(logo, (4, (h - logo.height) // 2))
    seg1.alpha_composite(name, (logo.width - 2, (h - name.height) // 2))
    seg2 = Image.new("RGBA", (max(110, sc.width + 30), h), GOLD + (255,))
    seg2.alpha_composite(sc, ((seg2.width - sc.width) // 2, (h - sc.height) // 2))
    parts = [seg1, seg2]
    if live:
        lt = text("EN VIVO", "MontB.ttf", 24, WHITE, 0.06)
        seg3 = Image.new("RGBA", (lt.width + 54, h), RED + (255,))
        ImageDraw.Draw(seg3).ellipse([16, h // 2 - 7, 30, h // 2 + 7], fill=WHITE)
        seg3.alpha_composite(lt, (38, (h - lt.height) // 2))
        parts.append(seg3)
    out = Image.new("RGBA", (sum(p.width for p in parts), h), (0, 0, 0, 0))
    x = 0
    for p in parts:
        out.alpha_composite(p, (x, 0))
        x += p.width
    m = Image.new("L", out.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, out.width - 1, h - 1], radius=10, fill=255)
    out.putalpha(Image.fromarray(np.minimum(np.asarray(out.getchannel("A")), np.asarray(m))))
    return out


def tag():
    """Our own 'BUEN FIN' tag (not the official logo)."""
    t1 = text("BUEN FIN", ANTON, 46, NAVY2, 0.02)
    t2 = text("EN FOOTBALL FRENZY", "MontB.ttf", 15, NAVY2, 0.08)
    w = max(t1.width, t2.width) + 36
    b = Image.new("RGBA", (w, t1.height + t2.height + 34), CREAM + (255,))
    b.alpha_composite(t1, ((w - t1.width) // 2, 10))
    b.alpha_composite(t2, ((w - t2.width) // 2, 14 + t1.height))
    ImageDraw.Draw(b).rectangle([0, b.height - 8, w, b.height], fill=RED)
    return b.rotate(4, Image.BICUBIC, expand=True)


def lower_third(label, headline):
    a = box(text(label, ANTON, 32, NAVY2, 0.03), GOLD, 18, 8)
    b = box(text(headline, ANTON, 50, NAVY2, 0.02), CREAM, 20, 10)
    out = Image.new("RGBA", (max(a.width, b.width), a.height + b.height), (0, 0, 0, 0))
    out.alpha_composite(a, (0, 0))
    out.alpha_composite(b, (0, a.height))
    return out


def jersey(name, h, rot=0):
    im = Image.open(g.SRC + name).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    p = 50
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (p + 8, p + 18))
    a = a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.6))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 8, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(im, (p, p))
    return out.rotate(rot, Image.BICUBIC, expand=True) if rot else out


class Confetti:
    def __init__(self, seed, n=110):
        r = np.random.default_rng(seed)
        self.x = r.uniform(0, W, n)
        self.y0 = r.uniform(-500, -20, n)
        self.vy = r.uniform(260, 520, n)
        self.sw = r.uniform(20, 60, n)
        self.ph = r.uniform(0, 6.28, n)
        self.size = r.uniform(10, 20, n)
        pal = [GOLD, CREAM, RED, (80, 140, 255), WHITE]
        self.col = [pal[i % len(pal)] for i in r.integers(0, 5, n)]

    def draw(self, c, dt):
        if dt < 0 or dt > 3.5:
            return
        d = ImageDraw.Draw(c)
        for i in range(len(self.x)):
            y = self.y0[i] + self.vy[i] * dt
            if y < -30 or y > H + 30:
                continue
            x = self.x[i] + self.sw[i] * math.sin(dt * 3 + self.ph[i])
            s = self.size[i]
            k = abs(math.sin(dt * 5 + self.ph[i]))
            d.rectangle([x, y, x + s, y + s * 0.4 + s * 0.6 * k], fill=self.col[i])


# ------------------------------------------------------------------ assets
BG = stadium()
TAG = tag()
SB = {s: scoreboard(s) for s in ("0 × 0", "1 × 0", "2 × 0")}
SB["FINAL"] = scoreboard("2 × 0", live=False)
FT = box(text("FINAL", "MontB.ttf", 24, WHITE, 0.1), (30, 30, 34), 16, 22)
L = {
    "t1": cream("BUEN FIN", 190, 0.01), "t2": gold_text("EN FOOTBALL", 150), "t3": gold_text("FRENZY", 150),
    "lt1": lower_third("EN VIVO · BUEN FIN", "ARRANCA EL PARTIDO"),
    "3x2": gold_text("3x2", 330), "s3": cream("EN TODAS LAS JERSEYS", 64, 0.02), "gol": cream("¡GOLAZO!", 110, 0.02),
    "lt2": lower_third("PRIMER GOL", "3 JERSEYS POR $1,600"),
    "5x3": gold_text("5x3", 330), "s5": cream("ARMA TU EQUIPO DE 5", 64, 0.02), "dob": cream("¡DOBLETE!", 110, 0.02),
    "lt3": lower_third("SEGUNDO GOL", "5 JERSEYS POR $2,400"),
    "gan": cream("GANAS TÚ", 180, 0.01), "auto": gold_text("3x2 y 5x3 AUTOMÁTICOS", 70),
    "env": cream("ENVÍO GRATIS A TODO MÉXICO", 52, 0.03), "hasta": cream("HASTA EL 1 DE DICIEMBRE", 44, 0.05),
    "cta": box(text("PIDE EN FOOTBALLFRENZY.SHOP O POR DM", "MontB.ttf", 30, NAVY2, 0.04), CREAM, 26, 18),
    "logo": badge(190),
}
J3 = [jersey("spotify/golf.png", 400, 6), jersey("mex_gold.png", 440), jersey("cl_rm_away26.png", 400, -6)]
J5 = [jersey(n, h, r) for n, h, r in [("fcb_0809_home.png", 300, 8), ("viejo/ame1213.png", 320, 4), ("portugal/pt2004_cr7.png", 360, 0),
                                       ("kaka.png", 320, -4), ("rm_1112_home.png", 300, -8)]]
CONF = [Confetti(1), Confetti(2), Confetti(3, 70)]


def pop(c, lay, x, y, t, t0, dur=0.45):
    k = back(t, t0, dur)
    if k > 0.01:
        put(c, lay, x, y, alpha=min(1, ease(t, t0, 0.2)), scale=max(0.05, k))


def slide_in(c, lay, x, y, t, t0, dy=260, dur=0.5):
    k = ease(t, t0, dur)
    if k > 0.01:
        put(c, lay, x, y + dy * (1 - k), alpha=k)


def frame(t):
    c = BG.copy()
    # scoreboard + tag
    sc = "0 × 0" if t < G1 else "1 × 0" if t < G2 else "2 × 0" if t < G3 else "FINAL"
    sb = SB[sc]
    bump = 1 + 0.12 * max(0, 1 - abs(t - (G1 + 0.15)) * 6) + 0.12 * max(0, 1 - abs(t - (G2 + 0.15)) * 6)
    put(c, sb, 50 + sb.width / 2, 70, scale=bump)
    if sc == "FINAL":
        c.alpha_composite(FT, (50 + sb.width + 8, 70 - FT.height // 2))
    put(c, TAG, W - 30 - TAG.width / 2, 92)

    if t < G1:                                   # kick-off
        pop(c, L["t1"], W / 2, 470, t, 0.2)
        slide_in(c, L["t2"], W / 2, 650, t, 0.55, 120)
        slide_in(c, L["t3"], W / 2, 800, t, 0.75, 120)
        slide_in(c, L["lt1"], 50 + L["lt1"].width / 2, 1180, t, 1.1, 80)
    elif t < G2:                                  # goal 1: 3x2
        lt = t - G1
        CONF[0].draw(c, lt)
        pop(c, L["3x2"], W / 2, 330, lt, 0.1, 0.5)
        slide_in(c, L["s3"], W / 2, 520, lt, 0.45, 60)
        pop(c, L["gol"], W / 2, 625, lt, 0.7)
        for i, (j, x) in enumerate(zip(J3, (230, 540, 850))):
            slide_in(c, j, x, 900 + (20 if i != 1 else 0), lt, 0.9 + 0.15 * i, 380)
        slide_in(c, L["lt2"], 50 + L["lt2"].width / 2, 1200, lt, 1.5, 80)
    elif t < G3:                                  # goal 2: 5x3
        lt = t - G2
        CONF[1].draw(c, lt)
        pop(c, L["5x3"], W / 2, 330, lt, 0.1, 0.5)
        slide_in(c, L["s5"], W / 2, 520, lt, 0.45, 60)
        pop(c, L["dob"], W / 2, 625, lt, 0.7)
        for i, (j, x) in enumerate(zip(J5, (150, 345, 540, 735, 930))):
            slide_in(c, j, x, 900 + abs(i - 2) * 25, lt, 0.85 + 0.12 * i, 380)
        slide_in(c, L["lt3"], 50 + L["lt3"].width / 2, 1200, lt, 1.6, 80)
    else:                                         # full time: CTA
        lt = t - G3
        CONF[2].draw(c, lt)
        pop(c, L["gan"], W / 2, 330, lt, 0.1, 0.5)
        slide_in(c, L["auto"], W / 2, 510, lt, 0.4, 60)
        slide_in(c, L["env"], W / 2, 600, lt, 0.6, 60)
        slide_in(c, L["hasta"], W / 2, 670, lt, 0.75, 60)
        pop(c, L["logo"], W / 2, 900, lt, 0.9, 0.5)
        slide_in(c, L["cta"], W / 2, 1150, lt, 1.2, 80)

    # white goal flash
    for gt in (G1, G2, G3):
        k = max(0, 1 - abs(t - gt) / 0.12)
        if k > 0:
            c = Image.blend(c, Image.new("RGBA", c.size, (255, 255, 255, 255)), 0.85 * k)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = OUT + "buen-fin-partido.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                           "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        ff.stdin.write(frame(i / FPS).convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    for name, ts in (("01", 2.6), ("02", 5.8), ("03", 9.4), ("04", 12.5)):
        frame(ts).convert("RGB").save(OUT + f"still-{name}.jpg", quality=90)
    print(out)
