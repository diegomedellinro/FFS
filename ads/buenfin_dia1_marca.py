"""Buen Fin día previo, versión con estilo de marca (negro + rojo, grano) y jerseys nuevas:
  #1 historia 'MAÑANA ARRANCA' (1080x1920) con espacio para el sticker de cuenta regresiva.
  #2 reel 'El combo perfecto de 3' (1080x1920, 9 s).
Uso: python3 buenfin_dia1_marca.py
"""
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text, ease, back, background, INK
from hf_ads import badge
from chat_doctor import emoji
from buenfin_logo import jersey, shadow

OUT = g.HERE + "out/buenfin_dia1_marca/"
W, H = 1080, 1920
RED, RED2, WHITE, GREY = (226, 20, 32), (150, 10, 18), (255, 255, 255), (170, 170, 176)


def bg():
    c = background(W, H, glows=((0.5, 0.62, 0.75, RED2, 0.75), (0.5, 0.08, 0.5, RED2, 0.35))).copy()
    d = ImageDraw.Draw(c)
    for y in (70, H - 70):                      # thin red rules top/bottom
        d.line([(60, y), (W - 60, y)], fill=RED + (255,), width=3)
    return c


def red(s, px, track=0.0):
    return shadow(text(s, "Anton.ttf", px, RED, track), 0.6, 12)


def white(s, px, track=0.0, font="Anton.ttf", col=WHITE):
    return shadow(text(s, font, px, col, track), 0.6, 10)


def pill(s, px, fg=WHITE, bg_=RED):
    t = text(s, "Anton.ttf", px, fg, 0.02)
    b = Image.new("RGBA", (t.width + 64, t.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, b.width - 1, b.height - 1], radius=b.height // 2, fill=bg_ + (255,))
    b.alpha_composite(t, (32, 15))
    return b


def outline_pill(s, px):
    t = text(s, "Anton.ttf", px, WHITE, 0.03)
    b = Image.new("RGBA", (t.width + 64, t.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, b.width - 1, b.height - 1], radius=b.height // 2, outline=RED + (255,), width=4)
    b.alpha_composite(t, (32, 15))
    return b


def mystery(name, h, rot):
    """Black silhouette with red rim and a white '?'."""
    j = jersey(name, h, rot)
    a = j.getchannel("A")
    sil = Image.new("RGBA", j.size, (14, 14, 16, 255))
    sil.putalpha(a.point(lambda v: 255 if v > 200 else 0))
    rim = sil.getchannel("A").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    glow = Image.new("RGBA", j.size, RED + (255,))
    glow.putalpha(rim.filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(255, v * 2)))
    out = Image.new("RGBA", j.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(sil)
    out.alpha_composite(glow.copy().filter(ImageFilter.GaussianBlur(1)))
    q = red("?", int(h * 0.5))
    out.alpha_composite(q, ((out.width - q.width) // 2, (out.height - q.height) // 2))
    return out


def story():
    c = bg()
    put(c, badge(230), W / 2, 300)
    put(c, white("13 AL 17 DE NOVIEMBRE", 40, 0.1, "MontB.ttf", GREY), W / 2, 470)
    put(c, white("MAÑANA ARRANCA EL", 120, 0.01), W / 2, 610)
    put(c, red("BUEN FIN", 250, 0.01), W / 2, 800)
    pl = pill("ESPERA NUEVAS PROMOCIONES", 48)
    em = emoji("🙌", 64)
    row = Image.new("RGBA", (pl.width + 16 + em.width, max(pl.height, em.height)), (0, 0, 0, 0))
    row.alpha_composite(pl, (0, (row.height - pl.height) // 2))
    row.alpha_composite(em, (pl.width + 16, (row.height - em.height) // 2))
    put(c, row, W / 2, 1010)
    for x, n, r, k in ((W / 2 - 300, "encargo/pumas.png", 8, 0.85), (W / 2 + 300, "encargo/tigres.png", -8, 0.85), (W / 2, "encargo/cruzazul.png", 0, 1.0)):
        put(c, mystery(n, int(330 * k), r), x, 1290 + (1 - k) * 60)
    # 1560-1740 free for the countdown sticker
    put(c, outline_pill("ACTIVA EL RECORDATORIO", 46), W / 2, 1540)
    put(c, white("FOOTBALLFRENZY.SHOP · PIDE POR DM", 30, 0.08, "MontB.ttf"), W / 2, 1800)
    return c


# ------------------------------------------------------------------ reel
FPS, DUR = 30, 9.0
COMBO = [("america110.png", -7), ("encargo/atlante.png", 0), ("encargo/chivas.png", 7)]
BG = bg()
J = [jersey(n, 380, r) for n, r in COMBO]
TAG = pill("$800", 54)
PLUS = red("+", 130)
T = {
    "h1": white("EL COMBO", 150, 0.01), "h2": red("PERFECTO DE 3", 130),
    "old": text("$2,400", "Anton.ttf", 120, GREY, 0.0, strike=RED), "new": white("$1,600", 270),
    "s": red("PAGAS 2, TE LLEVAS 3", 82, 0.02),
    "auto": pill("3x2 AUTOMÁTICO EN EL CARRITO · ENVÍO GRATIS", 40),
    "q": white("¿CUÁL SERÍA TU COMBO?", 96, 0.01), "c": red("COMENTA TUS 3", 116),
    "logo": badge(240), "url": white("FOOTBALLFRENZY.SHOP · BUEN FIN 13–17 NOV", 34, 0.06, "MontB.ttf"),
}
POS = [(W / 2, 660), (W / 2, 1020), (W / 2, 1380)]


def slide_in(c, lay, x, y, t, t0, dx=0, dy=200, dur=0.45):
    k = ease(t, t0, dur)
    if k > 0.01:
        put(c, lay, x + dx * (1 - k), y + dy * (1 - k), alpha=k)


def pop(c, lay, x, y, t, t0, dur=0.4):
    k = back(t, t0, dur)
    if k > 0.01:
        put(c, lay, x, y, alpha=min(1, ease(t, t0, 0.15)), scale=max(0.05, k))


def frame(t):
    c = BG.copy()
    if t < 5.2:
        slide_in(c, T["h1"], W / 2, 200, t, 0.0, dy=-120)
        slide_in(c, T["h2"], W / 2, 340, t, 0.2, dy=-120)
        for i, (j, (x, y)) in enumerate(zip(J, POS)):
            t0 = 0.6 + i * 0.9
            side = -1 if i % 2 == 0 else 1
            slide_in(c, j, x - 140 * side, y, t, t0, dx=side * -700, dy=0, dur=0.5)
            pop(c, TAG, x + 250 * (1 if i % 2 == 0 else -1), y + 110, t, t0 + 0.35)
            if i < 2:
                pop(c, PLUS, W / 2 + 40 * side, y + 180, t, t0 + 0.6)
        if t > 3.6:
            k = ease(t, 3.6, 0.4)
            c.alpha_composite(Image.new("RGBA", c.size, INK + (int(215 * k),)))
            pop(c, T["old"], W / 2, 820, t, 3.75)
            pop(c, T["new"], W / 2, 1030, t, 4.1, 0.5)
            slide_in(c, T["s"], W / 2, 1240, t, 4.5, dy=80)
    else:
        lt = t - 5.2
        pop(c, T["q"], W / 2, 560, lt, 0.0)
        pop(c, T["c"], W / 2, 695, lt, 0.25)
        pop(c, T["logo"], W / 2, 1000, lt, 0.5, 0.5)
        slide_in(c, T["auto"], W / 2, 1260, lt, 0.8, dy=80)
        slide_in(c, T["url"], W / 2, 1350, lt, 1.0, dy=80)
    if t < 0.25:
        c = Image.blend(Image.new("RGBA", c.size, (0, 0, 0, 255)), c, t / 0.25)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    story().convert("RGB").save(OUT + "1-story-manana-arranca.jpg", quality=94, subsampling=0)
    out = OUT + "2-reel-combo-de-3.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                           "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(frame(i / FPS).convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    for name, ts in (("a", 3.4), ("b", 5.0), ("c", 8.5)):
        frame(ts).convert("RGB").save(OUT + f"reel-still-{name}.jpg", quality=88)
    print("ok")
