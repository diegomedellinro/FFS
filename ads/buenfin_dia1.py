"""Buen Fin día previo (jueves 12):
  #1 historia 'MAÑANA ARRANCA' (1080x1920) con jerseys en silueta y espacio para el sticker de cuenta regresiva.
  #2 reel 'El combo perfecto de 3' (1080x1920, 9 s): 3 jerseys entran con su precio y se suman a $1,600.
Uso: python3 buenfin_dia1.py
"""
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, text, ease, back
from hf_ads import badge
from buenfin_logo import stadium, gold, logo, jersey, shadow, pill, CREAM, GOLD, NAVY2, WHITE

OUT = g.HERE + "out/buenfin_dia1/"
W, H = 1080, 1920
RED = (220, 32, 44)


def mystery(name, h, rot):
    """Jersey as a dark silhouette with a gold '?' on top."""
    j = jersey(name, h, rot)
    a = j.getchannel("A")
    sil = Image.new("RGBA", j.size, (20, 34, 78, 255))
    sil.putalpha(a.point(lambda v: int(v * 0.92)))
    rim = a.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5)).point(lambda v: min(255, v * 2))
    glow = Image.new("RGBA", j.size, GOLD + (255,))
    glow.putalpha(rim.point(lambda v: int(v * 0.55)))
    out = Image.new("RGBA", j.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
    out.alpha_composite(glow)
    q = gold("?", int(h * 0.55))
    out.alpha_composite(q, ((out.width - q.width) // 2, (out.height - q.height) // 2))
    return out


def story():
    c = stadium(W, H)
    put(c, logo(330), W / 2, 330)
    put(c, shadow(text("MAÑANA", "Anton.ttf", 190, CREAM, 0.01)), W / 2, 640)
    put(c, gold("ARRANCA", 190), W / 2, 830)
    put(c, pill("3x2 Y 5x3 EN TODAS LAS JERSEYS", 44, NAVY2, CREAM), W / 2, 990)
    for x, n, r, k in ((W / 2 - 300, "fcb_0809_home.png", 8, 0.85), (W / 2 + 300, "rm_1112_home.png", -8, 0.85), (W / 2, "kaka.png", 0, 1.0)):
        put(c, mystery(n, int(330 * k), r), x, 1250 + (1 - k) * 60)
    # clean space ~1480-1700 left free for Instagram's countdown sticker
    put(c, text("ACTIVA EL RECORDATORIO 🔔".replace(" 🔔", ""), "Anton.ttf", 54, GOLD, 0.04), W / 2, 1490)
    put(c, badge(100), W / 2 - 260, 1800)
    put(c, text("FOOTBALLFRENZY.SHOP", "MontB.ttf", 30, CREAM, 0.08), W / 2 + 60, 1800)
    return c


# ------------------------------------------------------------------ reel
FPS, DUR = 30, 9.0
COMBO = [("rm1718.png", -7), ("spotify/golf.png", 0), ("viejo/ame1213.png", 7)]
BG = stadium(W, H)
J = [jersey(n, 380, r) for n, r in COMBO]
TAG = pill("$800", 52, NAVY2, CREAM)
PLUS = gold("+", 120)
EQ = gold("=", 130)
T = {
    "h1": shadow(text("EL COMBO", "Anton.ttf", 150, CREAM, 0.01)), "h2": gold("PERFECTO DE 3", 130),
    "old": text("$2,400", "Anton.ttf", 120, (170, 170, 185), 0.0, strike=RED), "new": gold("$1,600", 260),
    "s": shadow(text("PAGAS 2, TE LLEVAS 3", "Anton.ttf", 78, CREAM, 0.02)),
    "auto": pill("3x2 AUTOMÁTICO EN EL CARRITO · ENVÍO GRATIS", 40, NAVY2, CREAM),
    "q": shadow(text("¿CUÁL SERÍA TU COMBO?", "Anton.ttf", 96, CREAM, 0.01)), "c": gold("COMENTA TUS 3", 110),
    "logo": badge(220), "url": shadow(text("FOOTBALLFRENZY.SHOP · BUEN FIN 13–17 NOV", "MontB.ttf", 34, CREAM, 0.06)),
}
POS = [(W / 2, 640), (W / 2, 1000), (W / 2, 1360)]   # stacked vertically on the reel


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
        slide_in(c, T["h1"], W / 2, 190, t, 0.0, dy=-120)
        slide_in(c, T["h2"], W / 2, 330, t, 0.2, dy=-120)
        for i, (j, (x, y)) in enumerate(zip(J, POS)):
            t0 = 0.6 + i * 0.9
            side = -1 if i % 2 == 0 else 1
            slide_in(c, j, x - 140 * side, y, t, t0, dx=side * -700, dy=0, dur=0.5)
            pop(c, TAG, x + 250 * (1 if i % 2 == 0 else -1), y + 110, t, t0 + 0.35)
            if i < 2:
                pop(c, PLUS, W / 2 + 40 * side, y + 180, t, t0 + 0.6)
        if t > 3.6:
            k = ease(t, 3.6, 0.4)
            ov = Image.new("RGBA", c.size, (4, 8, 24, int(200 * k)))
            c.alpha_composite(ov)
            pop(c, T["old"], W / 2, 820, t, 3.75)
            pop(c, T["new"], W / 2, 1020, t, 4.1, 0.5)
            slide_in(c, T["s"], W / 2, 1220, t, 4.5, dy=80)
    else:
        lt = t - 5.2
        pop(c, T["q"], W / 2, 560, lt, 0.0)
        pop(c, T["c"], W / 2, 690, lt, 0.25)
        pop(c, T["logo"], W / 2, 1000, lt, 0.5, 0.5)
        slide_in(c, T["auto"], W / 2, 1250, lt, 0.8, dy=80)
        slide_in(c, T["url"], W / 2, 1340, lt, 1.0, dy=80)
    # fade from black at start
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
