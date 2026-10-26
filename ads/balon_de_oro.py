"""Balón de Oro 2026 (lun 26 oct, 2:00 PM CDMX, London Palladium): carrusel de datos curiosos + historia, estética de marca
con acentos dorados.

Carrusel 1080x1350: portada → 5 datos → "¿Quién se lo lleva?" (comenta 1-4) → CTA 3x2.
Historia 1080x1920: "Hoy 2 PM · ¿Quién gana?" con espacio para el sticker de encuesta.
Uso: python3 balon_de_oro.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import text, rich, put, WHITE, INK
import abre_la_foto as b
from abre_la_foto import NEON, brush, crown, shop_box, caps, neon, jersey_glow, sign, SCRIPT

W, H = 1080, 1350
OUT = g.HERE + "out/balon_de_oro/"
GOLDN = (255, 190, 60)
SOFT = (200, 200, 206)


def gold_script(s, px, rot=6):
    lay = text(s, SCRIPT, px, (250, 246, 236)).rotate(rot, Image.BICUBIC, expand=True)
    return neon(lay, color=GOLDN, r=(10, 28), k=(1.3, 0.8))


def base(W=W, H=H, k=0.3):
    return g.background(W, H, ((0.5, 0.45, 0.8, (150, 10, 20), k), (0.5, 0.1, 0.5, (120, 80, 10), 0.18)), base=(6, 6, 7)).copy()


def ball(d):
    """Simple golden ball icon (drawn, no trademarked trophy)."""
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse([4, 4, d - 4, d - 4], fill=(236, 186, 70, 255), outline=(255, 226, 140, 255), width=max(3, d // 40))
    # pentagon + seams
    import math
    cx = cy = d / 2
    r = d * 0.17
    pts = [(cx + r * math.cos(math.radians(-90 + 72 * i)), cy + r * math.sin(math.radians(-90 + 72 * i))) for i in range(5)]
    dr.polygon(pts, fill=(170, 120, 30, 255))
    for x, y in pts:
        ex, ey = cx + (x - cx) * 2.5, cy + (y - cy) * 2.5
        dr.line([(x, y), (ex, ey)], fill=(170, 120, 30, 255), width=max(3, d // 45))
    hl = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([d * 0.2, d * 0.12, d * 0.5, d * 0.36], fill=(255, 255, 255, 90))
    im.alpha_composite(hl)
    return neon(im, color=GOLDN, r=(12, 34), k=(0.9, 0.6), drop=(0, 0))


def big(s, px=260):
    return neon(text(s, "Anton.ttf", px, (255, 236, 190)), color=GOLDN, r=(12, 36), k=(1.0, 0.7), drop=(0, 0))


def lines(c, rows, y, px=40, gap=56, color=WHITE):
    for i, s in enumerate(rows):
        put(c, text(s, "Inter-Bold.otf", px, color), W / 2, y + i * gap)


def cover():
    c = base()
    put(c, caps("HOY · 2:00 PM · LONDRES", 30, GOLDN, 0.35), W / 2, 100)
    put(c, gold_script("Balón de Oro", 190), W / 2, 270)
    put(c, brush(720, 20, 201), W / 2, 420, 1, 1, 3)
    put(c, ball(330), W / 2, 670)
    put(c, shop_box("5 DATOS QUE NO SABÍAS", 40), W / 2, 960)
    put(c, caps("DESLIZA  >>", 26, SOFT, 0.3), W / 2, 1060)
    sign(c, w=150, y=H - 80)
    return c


def dato(n, num, title_rows, sub_rows, jersey, jw=520, jh=470):
    c = base(k=0.28)
    put(c, caps(f"DATO {n} DE 5", 28, GOLDN, 0.35), W / 2, 90)
    put(c, big(num, 250 if len(num) <= 4 else 200), W / 2, 270)
    put(c, brush(560, 16, 210 + n, GOLDN), W / 2, 420, 1, 1, 3)
    lines(c, title_rows, 500, 46, 62)
    lines(c, sub_rows, 520 + 62 * len(title_rows), 34, 48, SOFT)
    if jersey:
        jersey_glow(c, jersey, W / 2, 975, jw, jh, 0)
    sign(c, w=120, y=H - 62)
    return c


DATOS = [
    ("8", ["Messi tiene 8 Balones de Oro"], ["Nadie en la historia ha ganado más.", "Cristiano lo sigue con 5."], "arg_last.png"),
    ("19", ["Si gana Lamine Yamal (19 años)"], ["sería el ganador más joven de la historia.", "El récord es de Ronaldo Nazário: 21 años, en 1997."], "cl_fcb_home26.png"),
    ("2001", ["El último inglés en ganarlo", "fue Michael Owen"], ["Harry Kane llega como favorito", "en las casas de apuestas."], "bayern.png"),
    ("0", ["Ningún mexicano lo ha ganado"], ["Este año Julián Quiñones está entre los 30", "nominados y el América Femenil compite como mejor club."], "mex_gold.png"),
    ("1956", ["Año del primer Balón de Oro"], ["Lo ganó Stanley Matthews.", "Y hoy, por primera vez, la gala es en Londres."], None),
]


def dato5_extra(c):
    put(c, ball(380), W / 2, 975)


def vota():
    c = base(k=0.34)
    put(c, gold_script("¿Quién se lo lleva?", 140, 5), W / 2, 170)
    put(c, text("Comenta tu número antes de las 2:00 PM", "Inter-Bold.otf", 40, WHITE), W / 2, 330)
    opts = (("1", "KANE", "bayern.png"), ("2", "YAMAL", "cl_fcb_home26.png"), ("3", "MBAPPÉ", "rm125.png"))
    for i, (num, name, j) in enumerate(opts):
        x = W * (0.2 + 0.3 * i)
        jersey_glow(c, j, x, 620, 290, 320, (-6, 0, 6)[i])
        put(c, big(num, 110), x, 840)
        put(c, caps(name, 32, WHITE, 0.2), x, 930)
    put(c, shop_box("4 · OTRO (DINOS QUIÉN)", 34), W / 2, 1050)
    put(c, caps("ETIQUETA A QUIEN SIEMPRE PIERDE LAS APUESTAS", 22, SOFT, 0.18), W / 2, 1140)
    sign(c, w=120, y=H - 62)
    return c


def cierre():
    c = base(k=0.38)
    put(c, gold_script("Lleva la jersey", 160, 5), W / 2, 190)
    put(c, gold_script("de tu ganador", 160, 5), W / 2, 350)
    for j, dx, rot in (("bayern.png", -0.3, -9), ("cl_fcb_home26.png", 0, 0), ("rm125.png", 0.3, 9)):
        jersey_glow(c, j, W / 2 + dx * W, 650, 330, 350, rot)
    put(c, rich((("LLEVA 3, ", WHITE), ("PAGA 2", NEON)), "Anton.ttf", 90), W / 2, 890)
    put(c, b.option(b.plane(72), "PÍDELA POR DM", "Te ayudamos con talla y dorsal"), W / 2, 1030)
    put(c, caps("FOOTBALLFRENZY.SHOP  ·  ENVÍO GRATIS  ·  S A 4XL", 24, SOFT, 0.16), W / 2, 1160)
    sign(c, w=130, y=H - 70)
    return c


def historia():
    SW, SH = 1080, 1920
    c = base(SW, SH, 0.34)
    put(c, b.logo(150), SW / 2, 300)
    put(c, caps("HOY · 2:00 PM", 32, GOLDN, 0.4), SW / 2, 420)
    put(c, gold_script("Balón de Oro", 210), SW / 2, 570)
    put(c, ball(260), SW / 2, 830)
    put(c, shop_box("¿QUIÉN SE LO LLEVA?", 40), SW / 2, 1030)
    # slot for the Instagram poll / quiz sticker
    w, h = 820, 300
    slot = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(slot)
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=40, fill=(255, 255, 255, 14), outline=(255, 190, 60, 200), width=3)
    put(c, slot, SW / 2, 1250)
    put(c, caps("PON AQUÍ EL STICKER DE ENCUESTA", 24, (150, 150, 156), 0.3), SW / 2, 1250)
    put(c, text("Kane · Yamal · Mbappé · Otro", "Inter-Bold.otf", 36, SOFT), SW / 2, 1450)
    put(c, caps("LA JERSEY DEL GANADOR, EN 3X2 >>", 26, WHITE, 0.2), SW / 2, 1530)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [cover]
    for i, (num, t, s, j) in enumerate(DATOS, 1):
        def f(i=i, num=num, t=t, s=s, j=j):
            c = dato(i, num, t, s, j)
            if j is None:
                dato5_extra(c)
            return c
        slides.append(f)
    slides += [vota, cierre]
    for i, fn in enumerate(slides, 1):
        fn().convert("RGB").save(f"{OUT}{i:02d}.jpg", quality=93, subsampling=0)
    historia().convert("RGB").save(f"{OUT}historia-encuesta.jpg", quality=93, subsampling=0)
    print(len(slides), "slides + historia")
