"""Video para historia 'Cómo hacer tu pedido en footballfrenzy.shop' (1080x1920, ~24 s).
Capturas reales de la tienda en celular (src/tutorial/), dentro de un teléfono, con toques animados.
Uso: python3 video_como_pedir.py
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import put, ease, back
from hf_ads import badge
from chat_doctor import emoji
from buenfin_dia1_marca import bg, red, white, pill, outline_pill, W, H, RED

OUT = g.HERE + "out/como_pedir/"
SRC = g.SRC + "tutorial/"
FPS = 30
PW = 700                                      # phone screen width
SCALE = PW / 1170
PH = round(1992 * SCALE)
PHONE_Y = 1130                                # phone centre

STEPS = [  # (caption lines, screen A, tap point on A in 1170x1992 px or None, screen B)
    (["ENTRA A FOOTBALLFRENZY.SHOP", "Y ELIGE TU LIGA"], "s01-home", (557, 1852), "s02-coleccion"),
    (["ELIGE TU JERSEY", "Y TU TALLA"], "t04-tallas", (310, 1129), "t04b-talla-m"),
    (["PERSONALÍZALA CON NOMBRE", "Y NÚMERO (OPCIONAL)"], "t05a-vacio", (423, 432), "t05-personaliza"),
    (["AGREGA 3 Y PAGA SOLO 2", "3x2 AUTOMÁTICO"], "t08-drawer3", (626, 1872), "t10-checkout"),
    (["LLENA TUS DATOS", "Y PAGA SEGURO"], "t11-pago", None, None),
]
INTRO, STEP, OUTRO = 2.4, 3.8, 3.6
DUR = INTRO + STEP * len(STEPS) + OUTRO


def screen(name):
    im = Image.open(SRC + name + ".png").convert("RGBA")
    im = im.resize((PW, round(im.height * SCALE)), Image.LANCZOS)
    m = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, PW - 1, PH - 1], radius=54, fill=255)
    return im, m


def phone_frame():
    b = 16
    f = Image.new("RGBA", (PW + 2 * b + 120, PH + 2 * b + 120), (0, 0, 0, 0))
    glow = Image.new("L", f.size, 0)
    ImageDraw.Draw(glow).rounded_rectangle([60, 60, 60 + PW + 2 * b, 60 + PH + 2 * b], radius=70, fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55))
    f.alpha_composite(Image.composite(Image.new("RGBA", f.size, RED + (255,)), Image.new("RGBA", f.size, (0, 0, 0, 0)), glow))
    d = ImageDraw.Draw(f)
    d.rounded_rectangle([60, 60, 60 + PW + 2 * b, 60 + PH + 2 * b], radius=70, fill=(22, 22, 26, 255), outline=(70, 70, 78, 255), width=3)
    return f


BG = bg()
FRAME = phone_frame()
SCR = {n: screen(n) for s in STEPS for n in (s[1], s[3]) if n}
CAP = [[white(l, 70 if i == 0 else 64, 0.01) if i == 0 else red(l, 66, 0.01) for i, l in enumerate(s[0])] for s in STEPS]
NUM = [pill(f"PASO {i + 1}", 44) for i in range(len(STEPS))]
SUB5 = white("TARJETA · OXXO · MERCADO PAGO · DEPÓSITO", 30, 0.05, "MontB.ttf")
HAND = emoji("👆", 90)
INTRO_T = {"logo": badge(260), "a": white("¿CÓMO HACER", 150, 0.01), "b": white("TU PEDIDO?", 150, 0.01),
           "c": red("EN 5 PASOS", 130, 0.01), "u": outline_pill("FOOTBALLFRENZY.SHOP", 52)}
OUT_T = {"a": white("ENVÍO GRATIS", 140, 0.01), "b": red("A TODO MÉXICO", 120, 0.01),
         "c": pill("3x2 Y 5x3 AUTOMÁTICOS EN EL CARRITO", 44), "logo": badge(260),
         "d": white("¿DUDAS? MÁNDANOS DM", 56, 0.02), "u": white("FOOTBALLFRENZY.SHOP", 40, 0.1, "MontB.ttf")}


def pop(c, lay, x, y, t, t0, dur=0.4):
    k = back(t, t0, dur)
    if k > 0.01:
        put(c, lay, x, y, alpha=min(1, ease(t, t0, 0.15)), scale=max(0.05, k))


def slide(c, lay, x, y, t, t0, dy=120, dur=0.45):
    k = ease(t, t0, dur)
    if k > 0.01:
        put(c, lay, x, y + dy * (1 - k), alpha=k)


def tap(c, x, y, lt, t0):
    """Hand + ripple at (x, y) on the canvas."""
    if lt < t0 - 0.35 or lt > t0 + 0.7:
        return
    k_in = ease(lt, t0 - 0.35, 0.3)
    hx, hy = x + 30, y + 60 + 40 * (1 - k_in)
    if lt >= t0:
        r = ease(lt, t0, 0.5)
        ring = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        rr = 20 + 70 * r
        ImageDraw.Draw(ring).ellipse([100 - rr, 100 - rr, 100 + rr, 100 + rr], outline=(255, 255, 255, int(255 * (1 - r))), width=8)
        dot = 26
        ImageDraw.Draw(ring).ellipse([100 - dot, 100 - dot, 100 + dot, 100 + dot], fill=(226, 20, 32, int(200 * (1 - r))))
        put(c, ring, x, y)
    put(c, HAND, hx, hy, alpha=k_in * (1 - ease(lt, t0 + 0.4, 0.3)))


def step_frame(c, i, lt):
    caps, a, tp, b = STEPS[i]
    # caption block
    pop(c, NUM[i], W / 2, 200, lt, 0.0, 0.35)
    for j, lay in enumerate(CAP[i]):
        slide(c, lay, W / 2, 300 + j * 88, lt, 0.12 + j * 0.1, dy=60, dur=0.35)
    # phone
    first = i == 0
    k = ease(lt, 0.0, 0.5) if first else 1.0
    py = PHONE_Y + 900 * (1 - k)
    put(c, FRAME, W / 2, py)
    top = py - PH / 2
    left = W / 2 - PW / 2
    cut = 1.7
    def show(name, k=1.0, scroll=0.0):
        im, m = SCR[name]
        y = round((im.height - PH) * scroll)
        v = im.crop((0, y, PW, y + PH))
        v.putalpha(m if k >= 1 else m.point(lambda q: int(q * k)))
        c.alpha_composite(v, (round(left), round(top)))
    if a == "t11-pago":                              # scroll down the payment methods
        show(a, scroll=ease(lt, 0.6, 2.4))
        slide(c, SUB5, W / 2, 1795, lt, 0.6, dy=40)
        return
    show(a)
    if b:
        kb = ease(lt, cut, 0.3)
        if kb > 0:
            show(b, kb)
    if tp:
        tap(c, left + tp[0] * SCALE, top + tp[1] * SCALE, lt, 1.25)
    if i == 3 and lt > cut + 0.4:                    # highlight the discounted total on checkout
        kk = ease(lt, cut + 0.4, 0.3)
        x0, y0 = left + 790 * SCALE, top + 175 * SCALE
        box = Image.new("RGBA", (int(370 * SCALE) + 20, int(170 * SCALE) + 20), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle([4, 4, box.width - 5, box.height - 5], radius=18, outline=RED + (int(255 * kk),), width=6)
        c.alpha_composite(box, (round(x0 - 10), round(y0 - 10)))
        pop(c, pill("DE $2,400 A SOLO $1,600", 46), W / 2, 1795, lt, cut + 0.5)


def frame(t):
    c = BG.copy()
    if t < INTRO:
        pop(c, INTRO_T["logo"], W / 2, 520, t, 0.0, 0.5)
        slide(c, INTRO_T["a"], W / 2, 820, t, 0.3)
        slide(c, INTRO_T["b"], W / 2, 990, t, 0.45)
        pop(c, INTRO_T["c"], W / 2, 1170, t, 0.75, 0.45)
        slide(c, INTRO_T["u"], W / 2, 1380, t, 1.0, dy=60)
    elif t < INTRO + STEP * len(STEPS):
        i = int((t - INTRO) // STEP)
        step_frame(c, i, t - INTRO - i * STEP)
    else:
        lt = t - INTRO - STEP * len(STEPS)
        pop(c, OUT_T["logo"], W / 2, 470, lt, 0.0, 0.5)
        slide(c, OUT_T["a"], W / 2, 760, lt, 0.3)
        slide(c, OUT_T["b"], W / 2, 910, lt, 0.45)
        pop(c, OUT_T["c"], W / 2, 1080, lt, 0.8)
        slide(c, OUT_T["d"], W / 2, 1290, lt, 1.1, dy=60)
        slide(c, OUT_T["u"], W / 2, 1380, lt, 1.25, dy=60)
    if t < 0.25:
        c = Image.blend(Image.new("RGBA", c.size, (0, 0, 0, 255)), c, t / 0.25)
    if t > DUR - 0.3:
        c = Image.blend(c, Image.new("RGBA", c.size, (0, 0, 0, 255)), (t - (DUR - 0.3)) / 0.3)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = OUT + "como-hacer-tu-pedido.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                           "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        ff.stdin.write(frame(n / FPS).convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    stills = [1.8] + [INTRO + i * STEP + 1.3 for i in range(5)] + [INTRO + 3 * STEP + 3.0, DUR - 0.6]
    for k, ts in enumerate(stills):
        frame(ts).convert("RGB").save(OUT + f"still-{k}.jpg", quality=85)
    print("ok", DUR)
