"""Historias 9:16 de la semana del 19 al 25 de octubre de 2026:
Champions (martes y miércoles), El Clásico (fin de semana) y promos 3x2 / 5x3.

Reusa los helpers de generar_ads.py. Cada historia es frame(W, H, t):
la imagen fija es t=99 y el video dura 8 s (el cuadro 0 ya muestra el titular).
Uso: python3 semana_clasico_champions.py [--video] [nombre ...]
"""
import math, os, sys
from PIL import ImageDraw
import generar_ads as g
from generar_ads import (Frame, background, stripes, head, text, rich, pill, product, put, ease, back,
                         footer, WHITE, RED, GREY, GOLD, INK, STORY)

OUT = g.HERE + "out/semana/"
BLAUGRANA = (40, 60, 170)
UCL_BLUE = (20, 40, 120)


def vs_badge(c, x, y, s, r=78):
    if s <= 0:
        return
    from PIL import Image
    b = Image.new("RGBA", (2 * r + 8, 2 * r + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.ellipse([4, 4, 2 * r + 4, 2 * r + 4], fill=INK, outline=WHITE, width=5)
    tv = text("VS", "Anton.ttf", 74, WHITE)
    b.alpha_composite(tv, ((b.width - tv.width) // 2, (b.height - tv.height) // 2))
    put(c, b, x, y, min(1, s * 1.4), max(0.3, s))


def clasico(W, H, t):
    """El Clásico este fin de semana: blanco contra blaugrana, con el 3x2."""
    L = Frame(W, H)
    c = background(W, H, ((0.2, 0.5, 0.55, (235, 235, 240), 0.22), (0.8, 0.5, 0.55, BLAUGRANA, 0.55), (0.5, 0.9, 0.5, RED, 0.3))).copy()
    head(c, L)
    put(c, pill("ESTE FIN DE SEMANA", "Anton.ttf", 44, RED, WHITE, 0.7, 0.3, track=0.06), L.cx, L.top + 95, 1)
    put(c, text("EL CLÁSICO", "Anton.ttf", 190, WHITE, 0.01), L.cx, 500, 1, 1 + 0.015 * math.sin(t * 2.5) if t < 99 else 1)
    q = rich((("¿Blanco ", WHITE), ("o ", GREY), ("blaugrana?", (150, 170, 255))), "Inter-Bold.otf", 52)
    put(c, q, L.cx, 650, 1)
    jy, jh, jw = 890, H * 0.20, W * 0.47
    a1, a2 = ease(t, 0.25, 0.6), ease(t, 0.55, 0.6)
    fl = lambda ph: math.sin(t * 1.5 + ph) * 7 if 1.2 < t < 99 else 0
    product(c, "rm125.png", W * 0.27 - (1 - a1) * W * 0.5, jy + fl(0), jw, jh, a1, 1, -5)
    product(c, "barca_away.png", W * 0.73 + (1 - a2) * W * 0.5, jy + fl(2), jw, jh, a2, 1, 5)
    vs_badge(c, L.cx, jy, back(t, 1.1, 0.5))
    a3 = ease(t, 1.6)
    put(c, text("REAL MADRID", "MontB.ttf", 34, WHITE, 0.12), W * 0.27, 1115, a3)
    put(c, text("BARÇA", "MontB.ttf", 34, (150, 170, 255), 0.12), W * 0.73, 1115, a3)
    a4 = ease(t, 2.1)
    put(c, rich((("$800 c/u", WHITE), ("  ·  ", GREY), ("Llévate las 2 + 1 GRATIS", RED)), "Inter-Bold.otf", 40), L.cx, 1205, a4)
    put(c, text("con el 3x2 en todas las jerseys", "Inter-SemiBold.otf", 32, GREY), L.cx, 1260, a4)
    footer(c, L, t, 2.6, label="ELIGE TU JERSEY", items=("Envío gratis", "Tallas S a 4XL", "Nombre y número"))
    return c


def encuesta(W, H, t):
    """Historia de interacción: deja espacio en medio para el sticker de encuesta de Instagram."""
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.35, 0.6, BLAUGRANA, 0.35), (0.5, 0.75, 0.6, RED, 0.35))).copy()
    c.alpha_composite(stripes(W, H, alpha=9))
    head(c, L)
    put(c, text("¿QUIÉN GANA", "Anton.ttf", 150, WHITE, 0.01), L.cx, 420, 1)
    put(c, rich((("EL ", WHITE), ("CLÁSICO", RED), ("?", WHITE)), "Anton.ttf", 150), L.cx, 580, 1)
    # jerseys small at both sides, middle stays empty for the poll sticker
    jy, jh, jw = 900, H * 0.17, W * 0.30
    a = ease(t, 0.3, 0.6)
    product(c, "rm125.png", W * 0.13 - (1 - a) * 300, jy, jw, jh, a, 1, -8)
    product(c, "barca_away.png", W * 0.87 + (1 - a) * 300, jy, jw, jh, a, 1, 8)
    a2 = ease(t, 1.2)
    put(c, text("Vota y comparte con tu rival", "Inter-Bold.otf", 40, WHITE), L.cx, 1230, a2)
    put(c, rich((("Jersey de tu equipo a $800 · ", GREY), ("3x2", RED), (" en todas", GREY)), "Inter-SemiBold.otf", 32), L.cx, 1285, a2)
    footer(c, L, t, 1.6, label="VER JERSEYS DEL CLÁSICO", items=("Envío gratis", "Tallas S a 4XL", "Pago seguro"))
    return c


def _champions(W, H, t, dia, jerseys):
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.3, 0.75, UCL_BLUE, 0.75), (0.5, 0.85, 0.5, RED, 0.25))).copy()
    # faint "stars" field (generic, no league logo)
    d = ImageDraw.Draw(c, 'RGBA')
    import random
    rnd = random.Random(3)
    for _ in range(70):
        x, y, r = rnd.random() * W, rnd.random() * H * 0.6, rnd.choice((1.5, 2, 2.5, 3))
        tw = 0.5 + 0.5 * math.sin(t * 3 + x) if t < 99 else 0.8
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(90 * tw)))
    head(c, L)
    put(c, pill(dia, "Anton.ttf", 50, WHITE, UCL_BLUE, 0.7, 0.3, track=0.08), L.cx, 345, 1)
    put(c, text("NOCHE DE", "Anton.ttf", 110, WHITE, 0.02), L.cx, 455, 1)
    put(c, text("CHAMPIONS", "Anton.ttf", 170, WHITE, 0.01), L.cx, 590, 1, 1 + 0.015 * math.sin(t * 2.4) if t < 99 else 1)
    put(c, text("Ve el partido con la jersey de tu equipo", "Inter-SemiBold.otf", 38, GREY), L.cx, 705, 1)
    gw, gh = W * 0.40, H * 0.115
    cy0 = 985
    for j, name in enumerate(jerseys):
        k = back(t, 0.3 + j * 0.25, 0.5)
        gx = L.cx + (-1 if j % 2 == 0 else 1) * W * 0.215
        gy = cy0 + (-1 if j < 2 else 1) * gh * 0.56
        product(c, name, gx, gy + (1 - min(1, k)) * 60, gw, gh, min(1, k * 1.4), 0.85 + 0.15 * min(1, k))
    a = ease(t, 1.6)
    put(c, rich((("LLEVA 3, PAGA 2", RED),), "Anton.ttf", 80), L.cx, 1265, a)
    put(c, text("Clubes de Europa, actuales y retro · $800 c/u", "Inter-SemiBold.otf", 32, WHITE), L.cx, 1325, a)
    footer(c, L, t, 2.0, label="ARMA TU 3X2", items=("Envío gratis", "Tallas S a 4XL", "Nombre y número"))
    return c


def champions_martes(W, H, t):
    return _champions(W, H, t, "MARTES", ["arsenal.png", "bayern.png", "juve.png", "psg4.png"])


def champions_miercoles(W, H, t):
    return _champions(W, H, t, "MIÉRCOLES", ["rm_away.png", "barca3.png", "kaka.png", "mu0708.png"])


def promo3x2(W, H, t):
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.45, 0.7, RED, 0.6),)).copy()
    c.alpha_composite(stripes(W, H, alpha=12))
    head(c, L)
    put(c, text("3X2", "Anton.ttf", 340, WHITE, 0.0), L.cx, 480, 1, 1 + 0.02 * math.sin(t * 3) if t < 99 else 1)
    put(c, text("EN TODAS LAS JERSEYS", "MontB.ttf", 42, WHITE, 0.14), L.cx, 690, 1)
    jy, jh, jw = 930, H * 0.17, W * 0.36
    for j, (name, dx, rot) in enumerate([("arsenal.png", -0.30, -9), ("barca3.png", 0.30, 9), ("rm125.png", 0, 0)]):
        k = ease(t, 0.3 + j * 0.3)
        product(c, name, L.cx + dx * W, jy + (16 if dx else -8) + (1 - k) * 90, jw * (1.12 if not dx else 1), jh * (1.12 if not dx else 1), k, 1, rot)
    s = back(t, 1.3, 0.5)
    if s > 0:
        put(c, pill("¡GRATIS!", "Anton.ttf", 56, RED, WHITE, 0.6, 0.3, outline=WHITE), L.cx + W * 0.14, jy - 140, min(1, s * 1.5), max(0.2, s), -8)
    a = ease(t, 1.8)
    old = text("$2,400", "Anton.ttf", 64, GREY, 0.02, strike=RED)
    new = text("$1,600", "Anton.ttf", 110, WHITE, 0.02)
    py = 1215
    put(c, text("3 JERSEYS POR", "MontB.ttf", 30, WHITE, 0.12), L.cx, py - 78, a)
    put(c, old, L.cx - new.width / 2 - old.width / 2 - 6, py + 10, a)
    put(c, new, L.cx + old.width / 2 - 6, py, a)
    put(c, text("Se aplica solo en el carrito · hasta el 31 de octubre", "Inter-SemiBold.otf", 30, WHITE), L.cx, py + 82, ease(t, 2.2))
    footer(c, L, t, 2.6, label="ARMA TU 3X2")
    return c


def promo5x3(W, H, t):
    L = Frame(W, H)
    c = background(W, H, ((0.5, 0.45, 0.7, (200, 150, 40), 0.35), (0.5, 0.7, 0.6, RED, 0.45))).copy()
    head(c, L)
    put(c, pill("PARA TODO EL EQUIPO", "Anton.ttf", 44, GOLD, INK, 0.7, 0.3, track=0.06), L.cx, 345, 1)
    put(c, text("5X3", "Anton.ttf", 300, WHITE, 0.0), L.cx, 575, 1, 1 + 0.02 * math.sin(t * 3) if t < 99 else 1)
    put(c, rich((("LLEVA 5, ", WHITE), ("PAGA 3", GOLD)), "Anton.ttf", 80), L.cx, 790, 1)
    # five jerseys fanned out
    names = ["juve.png", "bayern.png", "rm125.png", "barca_away.png", "arsenal.png"]
    jy, jh, jw = 985, H * 0.13, W * 0.30
    for j, name in enumerate(names):
        k = ease(t, 0.3 + j * 0.18)
        off = j - 2
        product(c, name, L.cx + off * W * 0.155, jy + abs(off) * 28 + (1 - k) * 90, jw, jh, k, 1, off * 7)
    a = ease(t, 1.8)
    old = text("$4,000", "Anton.ttf", 64, GREY, 0.02, strike=RED)
    new = text("$2,400", "Anton.ttf", 110, WHITE, 0.02)
    py = 1250
    put(c, text("5 JERSEYS POR", "MontB.ttf", 30, WHITE, 0.12), L.cx, py - 78, a)
    put(c, old, L.cx - new.width / 2 - old.width / 2 - 6, py + 10, a)
    put(c, new, L.cx + old.width / 2 - 6, py, a)
    put(c, rich((("Usa el código ", WHITE), ("5X3", GOLD), (" al pagar", WHITE)), "Inter-Bold.otf", 34), L.cx, py + 82, ease(t, 2.2))
    footer(c, L, t, 2.6, label="ARMA TU 5X3")
    return c


STORIES = {
    "1-martes-champions": champions_martes,
    "2-miercoles-champions": champions_miercoles,
    "3-promo-3x2": promo3x2,
    "4-promo-5x3": promo5x3,
    "5-clasico": clasico,
    "6-clasico-encuesta": encuesta,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(STORIES)
    W, H = STORY
    for n in names:
        fn = STORIES[n]
        fn(W, H, 99).convert("RGB").save(f"{OUT}{n}.jpg", quality=93, subsampling=0)
        print(n)
        if "--video" in sys.argv:
            g.CONCEPTS["_tmp"] = (fn, 8)
            g.OUT = OUT
            p = g.video("_tmp", STORY)
            os.replace(p, f"{OUT}{n}.mp4")
