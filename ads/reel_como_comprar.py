"""Reel "¿Cómo comprar tu jersey?" en 5 pasos, con capturas reales de footballfrenzy.shop (móvil, es-MX).

Formato 1080x1920 a 30 fps, sin audio (la música se agrega en Instagram).
Uso: python3 reel_como_comprar.py [--video] [--shots DIR]
Las capturas (1170x2532) se toman con Playwright; DIR por defecto: ads/src/reel/.
"""
import math, os, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import text, rich, pill, put, ease, back, WHITE, RED, INK, GREY, GOLD

W, H = 1080, 1920
FPS = 30
OUT = g.HERE + "out/reel/"
SHOTS = g.HERE + "src/reel/"
GREEN = (37, 211, 102)

# phone mockup: screen shows a window of the screenshot (shots are 1170 px wide)
PW, PH = 560, 840          # outer phone size on canvas
BEZ = 18                   # bezel
SW, SH = PW - 2 * BEZ, PH - 2 * BEZ
PHONE_Y = 1035             # phone centre y


@lru_cache(None)
def shot(name):
    im = Image.open(SHOTS + name).convert("RGB")
    return im.resize((SW, round(im.height * SW / im.width)), Image.LANCZOS)


@lru_cache(None)
def phone_frame():
    """Black phone body with rounded corners + soft shadow; returns (frame, screen mask)."""
    pad = 60
    fr = Image.new("RGBA", (PW + 2 * pad, PH + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", fr.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 24, pad + PW, pad + PH + 24], radius=78, fill=170)
    fr.putalpha(sh.filter(ImageFilter.GaussianBlur(28)))
    fr = Image.composite(Image.new("RGBA", fr.size, (0, 0, 0, 255)), Image.new("RGBA", fr.size, (0, 0, 0, 0)), fr.getchannel("A"))
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle([pad, pad, pad + PW, pad + PH], radius=78, fill=(28, 28, 32, 255), outline=(70, 70, 78, 255), width=3)
    mask = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, SW - 1, SH - 1], radius=62, fill=255)
    fr.pad = pad
    return fr, mask


def phone(c, name, y0, cy=PHONE_Y, alpha=1.0, dy=0, marks=(), scale=1.0):
    """Draw the phone with screenshot `name` scrolled to y0 (screen px). marks: (x0,y0,x1,y1,k) rings in screenshot px."""
    fr, mask = phone_frame()
    sc = shot(name)
    y0 = int(max(0, min(sc.height - SH, y0)))
    scr = sc.crop((0, y0, SW, y0 + SH)).convert("RGBA")
    if marks:
        ov = Image.new("RGBA", scr.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        f = SW / 1170
        for x0, a0, x1, a1, k in marks:
            if k <= 0.01:
                continue
            g_ = 10 * (1 - k)
            box = [x0 * f - 8 - g_, a0 * f - y0 - 8 - g_, x1 * f + 8 + g_, a1 * f - y0 + 8 + g_]
            d.rounded_rectangle(box, radius=26, outline=RED + (int(255 * min(1, k * 1.5)),), width=7)
        scr.alpha_composite(ov)
    lay = fr.copy()
    lay.paste(scr, (fr.pad + BEZ, fr.pad + BEZ), mask)
    # dynamic island
    ImageDraw.Draw(lay).rounded_rectangle([fr.pad + PW / 2 - 70, fr.pad + BEZ + 14, fr.pad + PW / 2 + 70, fr.pad + BEZ + 50], radius=18, fill=(0, 0, 0, 255))
    put(c, lay, W / 2, cy + dy, alpha, scale)


def tap(c, x, y, k, cy=PHONE_Y, y0=0):
    """Finger-tap ripple at screenshot coords (x, y) for progress k in [0,1]."""
    if not 0 < k < 1:
        return
    f = SW / 1170
    px = W / 2 - SW / 2 + x * f
    py = cy - SH / 2 + y * f - y0
    lay = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = 20 + 70 * k
    d.ellipse([110 - r, 110 - r, 110 + r, 110 + r], outline=(255, 255, 255, int(220 * (1 - k))), width=6)
    rr = 26 * (1 - k * 0.4)
    d.ellipse([110 - rr, 110 - rr, 110 + rr, 110 + rr], fill=(255, 255, 255, int(170 * (1 - k))))
    put(c, lay, px, py)


# ---------------------------------------------------------------- shared chrome

@lru_cache(None)
def bg():
    c = g.background(W, H, ((0.5, 0.5, 0.7, RED, 0.42), (0.1, 0.05, 0.5, RED, 0.18))).copy()
    c.alpha_composite(g.stripes(W, H, alpha=7))
    return c


def progress(c, step):
    """Five segments at the top: done/current are red."""
    seg, gap, y = 150, 14, 250
    x = W / 2 - (5 * seg + 4 * gap) / 2
    d = ImageDraw.Draw(c)
    for i in range(1, 6):
        col = RED if i <= step else (70, 70, 76)
        d.rounded_rectangle([x, y, x + seg, y + 10], radius=5, fill=col)
        x += seg + gap


def title(c, n, s, t, sub=None):
    a, b = back(t, 0.05, 0.45), ease(t, 0.15)
    put(c, pill(f"PASO {n}", "Anton.ttf", 40, RED, WHITE, track=0.06), W / 2, 330, a, 0.6 + 0.4 * a)
    lay = text(s, "Anton.ttf", 92 if len(s) < 20 else 80, WHITE, 0.01)
    put(c, lay, W / 2, 440 + (1 - b) * 40, b)
    if sub:
        put(c, text(sub, "Inter-SemiBold.otf", 36, GREY), W / 2, 515 + (1 - b) * 40, ease(t, 0.3))


def caption(c, parts, t, t0, y=1508):
    """Row of pills under the phone, popping one after another."""
    lays = [pill(s, "Inter-Bold.otf", 30, (255, 255, 255, 235) if not hot else RED, INK if not hot else WHITE, padx=0.6) for s, hot in parts]
    gap = 16
    rows, row, wsum = [], [], 0
    for l in lays:
        if row and wsum + l.width + gap > W - 80:
            rows.append(row); row, wsum = [], 0
        row.append(l); wsum += l.width + gap
    rows.append(row)
    k = 0
    for ri, row in enumerate(rows):
        tw = sum(l.width for l in row) + gap * (len(row) - 1)
        x = W / 2 - tw / 2
        for l in row:
            a = back(t, t0 + 0.12 * k, 0.4)
            put(c, l, x + l.width / 2, y + ri * 72, min(1, a), 0.7 + 0.3 * a)
            x += l.width + gap
            k += 1


def base(step):
    c = bg().copy()
    put(c, g.brand(26), W / 2, 190)
    if step:
        progress(c, step)
    return c


# ---------------------------------------------------------------- scenes (t = local time)

def hook(t):
    c = base(0)
    a = back(t, 0.0, 0.5)
    put(c, text("¿CÓMO COMPRAR", "Anton.ttf", 120, WHITE, 0.01), W / 2, 560, min(1, a), 0.8 + 0.2 * a)
    put(c, rich((("TU ", WHITE), ("JERSEY", RED), ("?", WHITE)), "Anton.ttf", 170), W / 2, 720, min(1, back(t, 0.25, 0.5)), 0.8 + 0.2 * min(1, back(t, 0.25, 0.5)))
    put(c, text("en 5 pasos", "Inter-Bold.otf", 52, WHITE), W / 2, 850, ease(t, 0.55))
    for i, (name, dx, rot) in enumerate((("rm125.png", -0.24, -10), ("america110.png", 0, 0), ("barca_away.png", 0.24, 10))):
        k = back(t, 0.35 + i * 0.12, 0.55)
        g.product(c, name, W / 2 + dx * W, 1170 + (1 - min(1, k)) * 160 + (30 if i != 1 else 0), 360, 380, min(1, k), 1, rot)
    put(c, pill("FOOTBALLFRENZY.SHOP", "Anton.ttf", 44, RED, WHITE, track=0.05), W / 2, 1440, ease(t, 0.9))
    return c


def paso1(t):
    c = base(1)
    title(c, 1, "ELIGE TU JERSEY", t, "205 modelos: clubes, selecciones y retro")
    k = ease(t, 0.2, 0.6)
    y0 = ease(t, 1.0, 2.0) * 330
    phone(c, "s1b-coleccion.png", y0, dy=(1 - k) * 300, alpha=k)
    # tap on the Real Madrid 125 card (preview coords 677, 1030)
    tap(c, 677 * 1.266, 1030 * 1.266, (t - 3.3) / 0.6, y0=y0)
    caption(c, (("Clubes", False), ("Selecciones", False), ("Retro", False), ("Mundial 2026", True)), t, 1.2)
    return c


def paso2(t):
    c = base(2)
    title(c, 2, "TALLA, VERSIÓN Y DORSAL", t)
    k = ease(t, 0.15, 0.6)
    y0 = 120
    f = 1170 / 924  # marks measured on the 924-wide preview
    marks = (
        (180 * f, 283 * f, 310 * f, 385 * f, ease(t, 0.9, 0.35)),
        (337 * f, 678 * f, 575 * f, 781 * f, ease(t, 1.8, 0.35)),
        (37 * f, 1067 * f, 888 * f, 1442 * f, ease(t, 2.7, 0.35)),
    )
    phone(c, "s2b-opciones.png", y0, dy=(1 - k) * 300, alpha=k, marks=marks)
    caption(c, (("Tallas S a 4XL", False), ("Aficionado o Jugador", False), ("Nombre y número", True)), t, 0.9)
    return c


PAGOS = (("Apple Pay", False), ("Tarjeta crédito o débito", False), ("Mercado Pago", False), ("Transferencia", True))


def paso3(t):
    c = base(3)
    title(c, 3, "AGREGA Y PAGA", t, "Pago seguro y encriptado")
    k = ease(t, 0.15, 0.6)
    f = 1170 / 924
    if t < 2.4:
        mark = (110 * f, 1850 * f, 888 * f, 1962 * f, ease(t, 1.0, 0.35))
        phone(c, "s3a-carrito.png", 330, dy=(1 - k) * 300, alpha=k, marks=(mark,))
        tap(c, 500 * f, 1905 * f, (t - 1.6) / 0.6, y0=330)
    else:
        sw = ease(t, 2.4, 0.35)
        marks = ((35 * f, 262 * f, 890 * f, 383 * f, ease(t, 2.9, 0.3)),
                 (35 * f, 1222 * f, 890 * f, 1381 * f, ease(t, 3.2, 0.3)),
                 (35 * f, 1381 * f, 890 * f, 1500 * f, ease(t, 3.5, 0.3)),
                 (35 * f, 1500 * f, 890 * f, 1615 * f, ease(t, 3.8, 0.3)))
        phone(c, "s3c-pago.png", 90, dy=(1 - sw) * 120, marks=marks)
    caption(c, PAGOS, t, 2.7)
    return c


@lru_cache(None)
def box_icon(s):
    """Simple drawn shipping box."""
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tan, dark, tape = (205, 150, 92), (170, 118, 68), (236, 214, 170)
    top = [(s * .5, s * .12), (s * .92, s * .3), (s * .5, s * .48), (s * .08, s * .3)]
    left = [(s * .08, s * .3), (s * .5, s * .48), (s * .5, s * .92), (s * .08, s * .74)]
    right = [(s * .5, s * .48), (s * .92, s * .3), (s * .92, s * .74), (s * .5, s * .92)]
    d.polygon(top, fill=(225, 175, 115))
    d.polygon(left, fill=tan)
    d.polygon(right, fill=dark)
    d.polygon([(s * .27, s * .21), (s * .71, s * .39), (s * .71, s * .5), (s * .27, s * .32)], fill=tape)
    d.polygon([(s * .6, s * .62), (s * .84, s * .52), (s * .84, s * .6), (s * .6, s * .7)], fill=RED)
    return im


def track_card(t):
    w, h = 900, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=40, fill=(255, 255, 255, 250))
    im.alpha_composite(text("TU PEDIDO VA EN CAMINO", "MontB.ttf", 30, RED, 0.12), (50, 42))
    im.alpha_composite(text("Código de rastreo", "Inter-SemiBold.otf", 32, (110, 110, 116)), (50, 110))
    code = "FF 2049 1187 MX"
    n = int(len(code) * ease(t, 1.0, 1.2))
    if n:
        im.alpha_composite(text(code[:n], "Anton.ttf", 70, INK, 0.04), (46, 150))
    # timeline
    steps = ("Preparado", "Enviado", "En camino", "Entregado")
    x0, x1, y = 70, w - 70, 340
    d.line([(x0, y), (x1, y)], fill=(225, 225, 228), width=8)
    p = ease(t, 1.6, 1.4) * 0.67
    d.line([(x0, y), (x0 + (x1 - x0) * p, y)], fill=RED, width=8)
    for i, s in enumerate(steps):
        x = x0 + (x1 - x0) * i / 3
        on = p >= i / 3 - 1e-6
        d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=RED if on else (225, 225, 228))
        lay = text(s, "Inter-Bold.otf", 26, INK if on else (150, 150, 155))
        im.alpha_composite(lay, (int(min(max(x - lay.width / 2, 20), w - 20 - lay.width)), y + 34))
    im.alpha_composite(text("Te llega por correo y WhatsApp", "Inter-SemiBold.otf", 30, (110, 110, 116)), (50, 440))
    return im


def paso4(t):
    c = base(4)
    title(c, 4, "PREPARAMOS Y ENVIAMOS", t, "Y te mandamos tu código de rastreo")
    k = back(t, 0.2, 0.55)
    bob = math.sin(t * 3) * 8 if t > 0.8 else 0
    put(c, box_icon(300), W / 2, 760 + bob + (1 - min(1, k)) * 120, min(1, k), 0.7 + 0.3 * min(1, k))
    a = ease(t, 0.6, 0.5)
    put(c, track_card(t), W / 2, 1180 + (1 - a) * 80, a)
    caption(c, (("Envío gratis", True), ("7 a 13 días hábiles", False)), t, 2.4, y=1530)
    put(c, text("*Código ilustrativo", "Inter-SemiBold.otf", 22, (120, 120, 126)), W / 2, 1600, ease(t, 2.4))
    return c


@lru_cache(None)
def photo(name, w, h, border=12):
    im = Image.open(g.SRC + name).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im = im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))
    out = Image.new("RGBA", (w + 2 * border, h + 2 * border), (255, 255, 255, 255))
    out.paste(im, (border, border))
    m = Image.new("L", out.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, out.width - 1, out.height - 1], radius=28, fill=255)
    out.putalpha(m)
    return out


def paso5(t):
    c = base(5)
    title(c, 5, "¡RECIBE TU PEDIDO!", t, "Fotos reales de nuestros clientes")
    a = back(t, 0.2, 0.55)
    put(c, photo("review_213636.jpg", 640, 560), W / 2 - 110, 860 + (1 - min(1, a)) * 200, min(1, a), 1, 4)
    b = back(t, 0.7, 0.55)
    put(c, photo("review_213712.jpg", 420, 526), W / 2 + 235, 1190 + (1 - min(1, b)) * 200, min(1, b), 1, -5)
    s = ease(t, 1.4)
    put(c, g.stars(54), W / 2 - 245, 1250, s)
    put(c, text("+3,000 pedidos", "Anton.ttf", 64, WHITE), W / 2 - 245, 1330, s)
    put(c, text("vendidos por Instagram", "Inter-SemiBold.otf", 28, GREY), W / 2 - 245, 1385, s)
    return c


def outro(t):
    c = base(0)
    a = back(t, 0.0, 0.5)
    put(c, text("ASÍ DE FÁCIL", "Anton.ttf", 140, WHITE, 0.01), W / 2, 470, min(1, a), 0.8 + 0.2 * min(1, a))
    for i, (name, dx, rot) in enumerate((("arg_last.png", -0.22, -9), ("rm125.png", 0.22, 9))):
        k = back(t, 0.2 + i * 0.12, 0.55)
        g.product(c, name, W / 2 + dx * W, 820 + (1 - min(1, k)) * 150, 420, 420, min(1, k), 1, rot)
    put(c, rich((("LLEVA 3, ", WHITE), ("PAGA 2", RED)), "Anton.ttf", 100), W / 2, 1110, ease(t, 0.5))
    put(c, text("y 5x3 con el código 5X3", "Inter-Bold.otf", 44, WHITE), W / 2, 1200, ease(t, 0.65))
    put(c, g.checks(("Envío gratis", "Tallas S a 4XL", "Pago seguro"), 30), W / 2, 1290, ease(t, 0.8))
    put(c, g.cta("COMPRA EN FOOTBALLFRENZY.SHOP", 900, 42), W / 2, 1420, ease(t, 0.95), 1 + 0.02 * math.sin(t * 5) * (t > 1.5))
    return c


SCENES = [(hook, 2.4), (paso1, 4.2), (paso2, 4.2), (paso3, 5.0), (paso4, 4.2), (paso5, 4.0), (outro, 3.4)]


def frame(t):
    for fn, d in SCENES:
        if t < d:
            return fn(t)
        t -= d
    return SCENES[-1][0](SCENES[-1][1])


def total():
    return sum(d for _, d in SCENES)


if __name__ == "__main__":
    if "--shots" in sys.argv:
        SHOTS = sys.argv[sys.argv.index("--shots") + 1].rstrip("/") + "/"
    os.makedirs(OUT, exist_ok=True)
    for fn, d in SCENES:
        fn(d - 0.01).convert("RGB").save(f"{OUT}still-{fn.__name__}.jpg", quality=90)
    print("stills ok")
    if "--video" in sys.argv:
        path = OUT + "como-comprar-reel-1080x1920.mp4"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(int(total() * FPS)):
            p.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        p.stdin.close()
        p.wait()
        print(path)
