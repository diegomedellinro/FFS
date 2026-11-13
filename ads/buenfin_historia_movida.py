"""Historia movida 'Cómo aprovechar el Buen Fin en footballfrenzy.shop' (1080x1920, ~15 s, cortes rápidos).
Usa las capturas reales de src/tutorial/ (las mismas del video 'cómo pedir').
Uso: python3 buenfin_historia_movida.py
"""
import math
import os
import subprocess
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, ease, back
from hf_ads import badge
from buenfin_logo import jersey
from buenfin_dia1_marca import bg, red, white, pill, outline_pill, W, H, RED
from video_como_pedir import SCR, FRAME, PW, PH, tap

OUT = g.HERE + "out/buenfin_movida/"
FPS, DUR = 30, 15.5
BG = bg()
CUTS = [1.2, 2.4, 3.3, 4.2, 5.1, 6.9, 8.7, 10.5, 12.3]      # scene starts (flash + shake on each)
SLAMS = CUTS + [0.15, 12.75, 13.3]


def slam(c, lay, x, y, t, t0, big=2.4, dur=0.2):
    if t < t0:
        return
    k = ease(t, t0, dur)
    s = big + (1 - big) * k
    if t > t0 + dur:                                   # small overshoot settle
        s = 1 + 0.04 * math.sin((t - t0 - dur) * 18) * math.exp(-(t - t0 - dur) * 9)
    put(c, lay, x, y, alpha=min(1, k * 1.6), scale=s)


def slide(c, lay, x, y, t, t0, dx=0, dy=120, dur=0.25):
    k = ease(t, t0, dur)
    if k > 0.01:
        put(c, lay, x + dx * (1 - k), y + dy * (1 - k), alpha=k)


def pop(c, lay, x, y, t, t0, dur=0.3, rot=0):
    k = back(t, t0, dur)
    if k > 0.01:
        put(c, lay, x, y, alpha=min(1, ease(t, t0, 0.1)), scale=max(0.05, k), rot=rot)


# ------------------------------------------------------------------ layers
L = {
    "buen": red("BUEN FIN", 300, 0.01), "fecha": pill("13 AL 17 DE NOVIEMBRE", 52),
    "como": white("¿CÓMO", 210, 0.01), "aprov": white("APROVECHARLO?", 150, 0.01),
    "url": outline_pill("FOOTBALLFRENZY.SHOP", 58),
    "3x2": red("3x2", 380), "3p": white("3 JERSEYS POR $1,600", 84, 0.01),
    "5x3": red("5x3", 380), "5p": white("5 JERSEYS POR $2,400", 84, 0.01),
    "50a": white("¿LLEVAS 2?", 120, 0.01), "50b": red("LA 2DA AL 50%", 150, 0.01),
    "code": pill("CÓDIGO: BUENFIN", 70),
    "auto": white("AUTOMÁTICO EN EL CARRITO", 60, 0.03),
    "envio": white("ENVÍO GRATIS", 160, 0.01), "mx": red("A TODO MÉXICO", 130, 0.01),
    "logo": badge(300), "pide": pill("PIDE YA EN FOOTBALLFRENZY.SHOP", 50),
    "hasta": white("SOLO HASTA EL 17 DE NOVIEMBRE", 44, 0.08, "MontB.ttf"),
}
STEP_TXT = [
    ("PASO 1", "ENTRA Y ELIGE TU LIGA"),
    ("PASO 2", "TALLA Y NOMBRE (OPCIONAL)"),
    ("PASO 3", "EL DESCUENTO SE APLICA SOLO"),
    ("PASO 4", "PAGA COMO QUIERAS"),
]
STEP_L = [(pill(a, 46), white(b, 74, 0.01)) for a, b in STEP_TXT]
JERS3 = [jersey(n, 290, r) for n, r in (("encargo/atlante.png", -10), ("rm1415_third_ls.png", 0), ("psg_home26.png", 10))]
JERS5 = [jersey(n, 225, r) for n, r in (("america110.png", -12), ("cl_rm_third26.png", -6), ("rm1415_third_ls.png", 0),
                                         ("psg_home26.png", 6), ("encargo/chivas.png", 12))]
JERS2 = [jersey(n, 340, r) for n, r in (("rm1415_third_ls.png", -6), ("psg_home26.png", 6))]
CHIPS = [pill(s, 34) for s in ("TARJETA", "OXXO", "MERCADO PAGO")]
PH_Y = 1135


def phone(c, t, t0, a, b=None, swipe_at=0.9, tp=None, scroll=False):
    """Phone in the middle; screen A, then swipe to B."""
    k = ease(t, t0, 0.25)
    py = PH_Y + 700 * (1 - k)
    put(c, FRAME, W / 2, py)
    top, left = py - PH / 2, W / 2 - PW / 2

    def show(name, dx=0, sc=0.0):
        im, m = SCR[name]
        y = round((im.height - PH) * sc)
        v = im.crop((0, y, PW, y + PH))
        v.putalpha(m)
        lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        lay.alpha_composite(v, (round(dx), 0))
        mm = m.copy()
        lay.putalpha(Image.composite(lay.getchannel("A"), Image.new("L", (PW, PH), 0), mm))
        c.alpha_composite(lay, (round(left), round(top)))

    lt = t - t0
    if scroll:
        show(a, sc=ease(lt, 0.3, 1.3))
        return
    if b and lt > swipe_at:
        ks = ease(lt, swipe_at, 0.25)
        show(a, dx=-PW * ks)
        show(b, dx=PW * (1 - ks))
    else:
        show(a)
    if tp:
        tap(c, left + tp[0] * PW / 1170, top + tp[1] * PW / 1170, lt, swipe_at - 0.15)


def scene(c, t):
    if t < CUTS[0]:                                     # BUEN FIN
        slam(c, L["buen"], W / 2, 860, t, 0.15)
        slide(c, L["fecha"], W / 2, 1100, t, 0.5)
    elif t < CUTS[1]:                                   # ¿CÓMO APROVECHARLO?
        lt = t - CUTS[0]
        slam(c, L["como"], W / 2, 720, lt, 0.0)
        slam(c, L["aprov"], W / 2, 920, lt, 0.2)
        slide(c, L["url"], W / 2, 1140, lt, 0.5)
    elif t < CUTS[2]:                                   # 3x2
        lt = t - CUTS[1]
        slam(c, L["3x2"], W / 2, 560, lt, 0.0)
        slide(c, L["3p"], W / 2, 830, lt, 0.15)
        for i, j in enumerate(JERS3):
            pop(c, j, W / 2 + (i - 1) * 290, 1250 + (40 if i != 1 else 0), lt, 0.2 + i * 0.1)
        slide(c, L["auto"], W / 2, 1560, lt, 0.4)
    elif t < CUTS[3]:                                   # 5x3
        lt = t - CUTS[2]
        slam(c, L["5x3"], W / 2, 560, lt, 0.0)
        slide(c, L["5p"], W / 2, 830, lt, 0.15)
        for i, j in enumerate(JERS5):
            pop(c, j, W / 2 + (i - 2) * 188, 1240 + abs(i - 2) * 30, lt, 0.15 + i * 0.07)
        slide(c, L["auto"], W / 2, 1560, lt, 0.4)
    elif t < CUTS[4]:                                   # 2da al 50%
        lt = t - CUTS[3]
        slam(c, L["50a"], W / 2, 520, lt, 0.0)
        slam(c, L["50b"], W / 2, 690, lt, 0.15)
        for i, j in enumerate(JERS2):
            pop(c, j, W / 2 + (i - 0.5) * 420, 1120, lt, 0.25 + i * 0.1)
        pop(c, L["code"], W / 2, 1520, lt, 0.45)
    elif t < CUTS[8]:                                   # 4 steps with the phone
        i = next(k for k in range(4) if t < CUTS[5 + k])
        t0 = CUTS[4 + i]
        lt = t - t0
        a, b = STEP_L[i]
        slam(c, a, W / 2, 190, lt, 0.0, big=1.8)
        slide(c, b, W / 2, 290, lt, 0.08, dy=60)
        if i == 0:
            phone(c, t, t0, "s01-home", "s02-coleccion", 0.9, (557, 1852))
        elif i == 1:
            phone(c, t, t0, "t04-tallas", "t05-personaliza", 0.9, (310, 1129))
        elif i == 2:
            phone(c, t, t0, "t08-drawer3", "t10-checkout", 1.0, (626, 1872))
            pop(c, pill("DE $2,400 A SOLO $1,600", 40), W / 2, 1805, lt, 1.2)
        else:
            phone(c, t, t0, "t11-pago", scroll=True)
            xs = [W / 2 - 300, W / 2 - 40, W / 2 + 270]
            for k, ch in enumerate(CHIPS[:3]):
                pop(c, ch, xs[k], 1805, lt, 0.4 + k * 0.18)
    else:                                               # CTA
        lt = t - CUTS[8]
        slam(c, L["envio"], W / 2, 520, lt, 0.0)
        slam(c, L["mx"], W / 2, 680, lt, 0.15)
        slam(c, L["logo"], W / 2, 1010, lt, 0.45, big=2.0)
        s = 1 + 0.05 * max(0, math.sin((lt - 1.0) * 6)) if lt > 1.0 else 1
        k = back(lt, 1.0, 0.3)
        if k > 0.01:
            put(c, L["pide"], W / 2, 1320, alpha=min(1, ease(lt, 1.0, 0.1)), scale=max(0.05, k) * s)
        slide(c, L["hasta"], W / 2, 1450, lt, 1.3, dy=50)


def frame(t):
    c = BG.copy()
    # moving red streaks in the background for energy
    d = ImageDraw.Draw(c)
    for k in range(6):
        x = ((t * 900 + k * 420) % (W + 900)) - 450
        d.line([(x, 0), (x - 500, H)], fill=(120, 10, 16, 255), width=10)
    scene(c, t)
    # shake + flash right after each cut / slam
    dx = dy = 0
    flash = 0.0
    for s in SLAMS:
        e = t - s
        if 0 <= e < 0.35:
            amp = 18 * math.exp(-e * 12)
            dx += amp * math.sin(e * 90)
            dy += amp * math.cos(e * 77)
    for s in CUTS:
        e = t - s
        if 0 <= e < 0.12:
            flash = max(flash, 1 - e / 0.12)
    z = 1.03
    big = c.resize((round(W * z), round(H * z)), Image.BILINEAR)
    ox, oy = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
    c = big.crop((round(ox), round(oy), round(ox) + W, round(oy) + H))
    if flash > 0:
        c = Image.blend(c, Image.new("RGBA", c.size, (255, 255, 255, 255)), 0.55 * flash)
    if t < 0.15:
        c = Image.blend(Image.new("RGBA", c.size, (0, 0, 0, 255)), c, t / 0.15)
    if t > DUR - 0.25:
        c = Image.blend(c, Image.new("RGBA", c.size, (0, 0, 0, 255)), (t - (DUR - 0.25)) / 0.25)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = OUT + "historia-buen-fin-movida.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                           "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        ff.stdin.write(frame(n / FPS).convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    stills = [0.9, 2.1, 3.0, 3.9, 4.9, 6.5, 8.3, 10.2, 12.0, 14.8]
    for k, ts in enumerate(stills):
        frame(ts).convert("RGB").save(OUT + f"still-{k}.jpg", quality=85)
    print("ok")
