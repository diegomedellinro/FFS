"""Historias del día del Clásico (dom 25 oct 2026, 2:00 PM CDMX, Spotify Camp Nou) con la estética de marca.

1-partido  — "Hoy · El Clásico · Barcelona vs Real Madrid" (inspirado en un post de agenda de partido)
2-quiz     — pregunta del Clásico con espacio para el sticker de Quiz de Instagram
3-respuesta— respuesta del quiz
4-3x2      — promo 3x2 con espacio para el sticker de enlace
Formato 1080x1920; el texto clave vive entre y≈250 y y≈1536 (zona segura de historias).
Uso: python3 clasico_historias.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import text, rich, put, WHITE, INK
from abre_la_foto import NEON, script, brush, crown, shop_box, caps, neon, jersey_glow, logo

W, H = 1080, 1920
OUT = g.HERE + "out/clasico_historias/"
SOFT = (200, 200, 206)


def bg(y=0.5, k=0.32):
    return g.background(W, H, ((0.5, y, 0.8, (150, 10, 20), k),), base=(6, 6, 7)).copy()


def sticker_slot(c, cy, w=760, h=330, label="AQUÍ VA EL STICKER"):
    """Dashed neon frame marking where to drop an Instagram sticker (it gets covered)."""
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1, r = 4, 4, w - 5, h - 5, 40
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=(255, 255, 255, 14))
    step = 34
    for x in range(x0 + r, x1 - r, step):
        for yy in (y0, y1):
            d.line([(x, yy), (min(x + 18, x1 - r), yy)], fill=(255, 70, 80, 255), width=4)
    for y in range(y0 + r, y1 - r, step):
        for xx in (x0, x1):
            d.line([(xx, y), (xx, min(y + 18, y1 - r))], fill=(255, 70, 80, 255), width=4)
    put(c, neon(lay, r=(6, 16), k=(0.8, 0.5), drop=(0, 0)), W / 2, cy)
    put(c, caps(label, 24, (150, 150, 156), 0.3), W / 2, cy)


def partido():
    c = bg(0.6, 0.36)
    put(c, logo(230), W / 2, 330)
    put(c, rich((("HOY 2:00 PM", WHITE), ("   |   SPOTIFY CAMP NOU", SOFT)), "MontB.ttf", 30), W / 2, 500)
    put(c, crown(120), W / 2 + 150, 590)
    put(c, script("El Clásico", 230, 6), W / 2, 720)
    put(c, brush(780, 20, 101), W / 2, 880, 1, 1, 3)
    put(c, shop_box("BARCELONA VS REAL MADRID", 34), W / 2, 975)
    jersey_glow(c, "cl_fcb_home26.png", W * 0.28, 1265, 440, 470, -6)
    jersey_glow(c, "rm125.png", W * 0.72, 1270, 440, 470, 6)
    put(c, neon(text("VS", "Anton.ttf", 96, WHITE)), W / 2, 1260)
    put(c, caps("¿CON QUÉ JERSEY LO VAS A VER?", 28, WHITE, 0.2), W / 2, 1500)
    return c


def quiz():
    c = bg(0.45, 0.34)
    put(c, logo(150), W / 2, 300)
    put(c, caps("QUIZ DEL CLÁSICO", 30, NEON, 0.4), W / 2, 420)
    put(c, script("¿Quién es el", 150, 5), W / 2, 540)
    put(c, script("máximo goleador", 150, 5), W / 2, 690)
    put(c, shop_box("EN LA HISTORIA DEL CLÁSICO?", 34), W / 2, 850)
    sticker_slot(c, 1150, label="PON AQUÍ EL STICKER DE QUIZ")
    put(c, text("La respuesta, en la siguiente historia", "Inter-SemiBold.otf", 34, SOFT), W / 2, 1410)
    jersey_glow(c, "cl_fcb_0809.png", 130, 1490, 230, 250, -12)
    jersey_glow(c, "cl_rm_1112.png", W - 130, 1490, 230, 250, 12)
    return c


def respuesta():
    c = bg(0.5, 0.38)
    put(c, logo(150), W / 2, 300)
    put(c, caps("RESPUESTA", 30, NEON, 0.4), W / 2, 420)
    put(c, script("Lionel Messi", 190, 5), W / 2, 570)
    put(c, brush(720, 20, 103), W / 2, 700, 1, 1, 3)
    put(c, neon(text("26", "Anton.ttf", 300, WHITE)), W / 2, 920)
    put(c, shop_box("GOLES EN CLÁSICOS", 38), W / 2, 1110)
    jersey_glow(c, "cl_fcb_1011ls.png", W / 2, 1340, 380, 330, 0)
    put(c, caps("¿ACERTASTE? CUÉNTANOS POR DM", 26, WHITE, 0.2), W / 2, 1530)
    return c


def promo():
    c = bg(0.5, 0.4)
    put(c, logo(150), W / 2, 300)
    put(c, caps("ESPECIAL CLÁSICO", 30, NEON, 0.4), W / 2, 420)
    put(c, script("Lleva 3", 210, 5), W / 2 - 40, 545)
    put(c, script("paga 2", 210, 5), W / 2 + 50, 730)
    for n, dx, rot, y in (("cl_rm_away26.png", -0.3, -9, 1010), ("cl_fcb_home26.png", 0, 0, 980), ("rm125.png", 0.3, 9, 1010)):
        jersey_glow(c, n, W / 2 + dx * W, y, 330, 350, rot)
    put(c, neon(text("GRATIS", "Anton.ttf", 40, WHITE)), W / 2 + 0.3 * W, 1190)
    put(c, shop_box("SE APLICA SOLO EN EL CARRITO", 30), W / 2, 1270)
    put(c, text("Y con el código 5X3: llevas 5, pagas 3", "Inter-SemiBold.otf", 34, SOFT), W / 2, 1350)
    sticker_slot(c, 1470, 860, 130, "STICKER DE ENLACE · FOOTBALLFRENZY.SHOP")
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("1-partido", partido), ("2-quiz", quiz), ("3-respuesta", respuesta), ("4-3x2", promo)):
        fn().convert("RGB").save(f"{OUT}{name}.jpg", quality=93, subsampling=0)
        print(name)
