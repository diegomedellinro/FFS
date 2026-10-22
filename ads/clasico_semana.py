"""Posts de la semana del Clásico (Barça vs Real Madrid, dom 25 oct 2026, 13:00 h CDMX) con la estética de marca.

P1 duelo  — carrusel "Duelo de jerseys": 5 rondas Madrid vs Barça, se vota comentando 1 o 2.
P2 retro  — carrusel "Las retro del Clásico": jerseys retro + el momento que las hizo icónicas.
P3 apuesta — post "La apuesta": si pierde tu equipo, me regalas la jersey (para etiquetar).
P4 despues — 3 posts para el lunes según el resultado (gana Madrid / gana Barça / empate).
P5 combos — carrusel "Arma tu 3x2 del Clásico".
Formato 1080x1350. Uso: python3 clasico_semana.py [p1 p2 ...]
"""
import os, sys
from PIL import Image, ImageFilter
import generar_ads as g
from generar_ads import text, rich, put, WHITE, INK
import abre_la_foto as b
from abre_la_foto import W, H, NEON, script, brush, crown, shop_box, caps, neon, jersey_glow, sign

OUT = g.HERE + "out/clasico_semana/"
SOFT = (200, 200, 206)


def base(glow=0.32, y=0.5):
    return b.bg(((0.5, y, 0.78, glow),))


def num(n, px=96):
    return neon(text(str(n), "Anton.ttf", px, WHITE))


def label(c, cx, y, team, sub):
    put(c, caps(team, 32), cx, y)
    put(c, text(sub, "Inter-SemiBold.otf", 28, SOFT), cx, y + 46)


def swipe(c, s="DESLIZA", y=1150):
    put(c, caps(s + "  >>", 26, SOFT, 0.3), W / 2, y)


# ---------------------------------------------------------------- P1 duelo de jerseys

ROUNDS = [
    ("Locales", "rm125.png", "Local 125 años", "cl_fcb_home26.png", "Local 26/27"),
    ("Visitantes", "cl_rm_away26.png", "Visitante 26/27", "barca_away.png", "Visitante 26/27"),
    ("Terceras", "cl_rm_third26.png", "Tercera 26/27", "cl_fcb_third26.png", "Tercera 26/27"),
    ("Retro", "cl_rm_1112.png", "Local 11/12", "cl_fcb_0809.png", "Local 08/09"),
    ("Especiales", "cl_rm_1617away.png", "Visitante 16/17", "cl_fcb_travis.png", "Edición Travis Scott"),
]


def p1_cover():
    c = base()
    put(c, crown(130), W / 2 + 70, 120)
    put(c, script("Duelo de", 190), W / 2 - 40, 250)
    put(c, script("jerseys", 220), W / 2 + 40, 420)
    put(c, shop_box("EDICIÓN CLÁSICO", 40), W / 2, 590)
    picks = (("cl_rm_away26.png", -0.33, -10), ("cl_fcb_home26.png", -0.11, -4), ("rm125.png", 0.11, 4), ("barca_away.png", 0.33, 10))
    for name, dx, rot in picks:
        jersey_glow(c, name, W / 2 + dx * W, 860, 330, 360, rot)
    put(c, rich((("5 RONDAS  ·  ", WHITE), ("TÚ ELIGES", NEON)), "Anton.ttf", 60), W / 2, 1090)
    swipe(c, "VOTA EN COMENTARIOS · DESLIZA", 1160)
    sign(c, w=150, y=H - 80)
    return c


def p1_round(i):
    name, lj, ls, rj, rs = ROUNDS[i]
    c = base(0.3, 0.55)
    put(c, caps(f"RONDA {i + 1} DE 5", 28, NEON, 0.3), W / 2, 95)
    put(c, script(name, 200, 5), W / 2, 230)
    put(c, brush(620, 16, 20 + i), W / 2, 345, 1, 1, 3)
    jersey_glow(c, lj, W * 0.285, 690, 470, 520, -6)
    jersey_glow(c, rj, W * 0.715, 700, 470, 520, 6)
    put(c, neon(text("VS", "Anton.ttf", 100, WHITE)), W / 2, 690)
    put(c, num(1), W * 0.285, 970)
    put(c, num(2), W * 0.715, 970)
    label(c, W * 0.285, 1060, "REAL MADRID", ls)
    label(c, W * 0.715, 1060, "BARÇA", rs)
    put(c, shop_box("COMENTA 1 O 2", 34), W / 2, 1195)
    sign(c, w=120, y=H - 62)
    return c


def p1_end():
    c = base(0.36)
    put(c, script("¿Quién ganó?", 190, 6), W / 2, 230)
    put(c, text("Deja tus 5 votos en comentarios, así:", "Inter-SemiBold.otf", 40, SOFT), W / 2, 420)
    put(c, neon(text("1  2  2  1  2", "Anton.ttf", 150, WHITE, 0.02)), W / 2, 560)
    put(c, brush(700, 18, 31), W / 2, 680, 1, 1, 2)
    put(c, text("Publicamos el marcador en historias", "Inter-Bold.otf", 40, WHITE), W / 2, 770)
    put(c, rich((("LLEVA 3, ", WHITE), ("PAGA 2", NEON)), "Anton.ttf", 84), W / 2, 920)
    put(c, caps("TODAS EN FOOTBALLFRENZY.SHOP", 30, WHITE, 0.2), W / 2, 1010)
    put(c, caps("ENVÍO GRATIS  ·  TALLAS S A 4XL  ·  PAGO SEGURO", 22, SOFT, 0.14), W / 2, 1065)
    sign(c, w=190, y=H - 120)
    return c


# ---------------------------------------------------------------- P2 retro

RETRO = [
    ("08/09", "cl_fcb_0809.png", "EL 2-6 EN EL BERNABÉU", "Barça · Local 08/09"),
    ("09/10", "cl_rm_0910.png", "LLEGA CRISTIANO", "Real Madrid · Local 09/10 manga larga"),
    ("10/11", "cl_fcb_1011ls.png", "LA MANITA EN EL CAMP NOU", "Barça · Local 10/11 manga larga"),
    ("11/12", "cl_rm_1112.png", "«CALMA, CALMA»", "Real Madrid · Local 11/12"),
    ("14/15", "cl_fcb_1415.png", "EL AÑO DEL TRIPLETE", "Barça · Local 14/15"),
    ("17/18", "cl_rm_1718ls.png", "LA TERCERA CHAMPIONS SEGUIDA", "Real Madrid · Local 17/18 manga larga"),
]


def p2_cover():
    c = base(0.3)
    put(c, caps("NOSTALGIA", 30, NEON, 0.4), W / 2, 100)
    put(c, script("Las retro", 220), W / 2 - 30, 250)
    put(c, script("del Clásico", 200), W / 2 + 30, 440)
    names = ("cl_fcb_0809.png", "cl_rm_1112.png", "cl_fcb_1415.png", "cl_rm_1718ls.png")
    for k, (n, dx, rot) in enumerate(zip(names, (-0.33, -0.11, 0.11, 0.33), (-10, -4, 4, 10))):
        jersey_glow(c, n, W / 2 + dx * W, 800, 320, 350, rot)
    put(c, shop_box("¿CON CUÁL TE QUEDAS?", 38), W / 2, 1050)
    swipe(c, "DESLIZA", 1140)
    sign(c, w=150, y=H - 80)
    return c


def p2_slide(i):
    yr, name, moment, sub = RETRO[i]
    c = base(0.3, 0.52)
    put(c, script(yr, 230, 6), W / 2, 200)
    put(c, brush(560, 16, 40 + i), W / 2, 315, 1, 1, 3)
    jersey_glow(c, name, W / 2, 690, 640, 600, 0)
    put(c, shop_box(moment, 34 if len(moment) < 22 else 28), W / 2, 1050)
    put(c, text(sub, "Inter-SemiBold.otf", 32, SOFT), W / 2, 1135)
    put(c, caps(f"{i + 1} / {len(RETRO)}", 22, SOFT, 0.3), W - 90, 70)
    sign(c, w=120, y=H - 62)
    return c


def p2_end():
    c = base(0.36)
    put(c, script("¿Cuál te falta?", 160, 6), W / 2, 240)
    put(c, text("Todas las retro del Clásico están en la tienda", "Inter-SemiBold.otf", 38, SOFT), W / 2, 420)
    for n, dx, rot in (("cl_rm_0910.png", -0.22, -8), ("cl_fcb_1011ls.png", 0.22, 8)):
        jersey_glow(c, n, W / 2 + dx * W, 680, 420, 400, rot)
    put(c, rich((("LLEVA 3, ", WHITE), ("PAGA 2", NEON)), "Anton.ttf", 84), W / 2, 950)
    put(c, caps("FOOTBALLFRENZY.SHOP  ·  PEDIDOS POR DM", 28, WHITE, 0.18), W / 2, 1040)
    sign(c, w=170, y=H - 110)
    return c


# ---------------------------------------------------------------- P3 apuesta

def p3():
    c = base(0.38, 0.55)
    put(c, crown(120), W / 2 + 120, 95)
    put(c, script("La apuesta", 220, 6), W / 2, 220)
    put(c, caps("SI PIERDE TU EQUIPO...", 44, WHITE, 0.16), W / 2, 400)
    jersey_glow(c, "rm125.png", W * 0.29, 700, 460, 500, -7)
    jersey_glow(c, "cl_fcb_home26.png", W * 0.71, 715, 460, 500, 7)
    put(c, neon(text("VS", "Anton.ttf", 96, WHITE)), W / 2, 700)
    put(c, shop_box("ME REGALAS LA JERSEY", 42), W / 2, 1000)
    put(c, script("Etiqueta a tu rival", 120, 3), W / 2, 1125)
    put(c, caps("DOMINGO 25 · 13:00 H", 24, SOFT, 0.3), W / 2, 1225)
    sign(c, w=110, y=H - 55)
    return c


# ---------------------------------------------------------------- P4 el día después

def p4(kind):
    c = base(0.36)
    if kind == "madrid":
        put(c, caps("GANÓ EL MADRID", 34, NEON, 0.3), W / 2, 110)
        put(c, script("Hoy se sale", 200, 5), W / 2 - 20, 250)
        put(c, script("de blanco", 210, 5), W / 2 + 30, 430)
        trio, tag = ("cl_rm_1718ls.png", "rm125.png", "cl_rm_1112.png"), "LA BLANCA SE PRESUME"
    elif kind == "barca":
        put(c, caps("GANÓ EL BARÇA", 34, NEON, 0.3), W / 2, 110)
        put(c, script("Hoy se sale", 200, 5), W / 2 - 20, 250)
        put(c, script("blaugrana", 210, 5), W / 2 + 30, 430)
        trio, tag = ("cl_fcb_1415.png", "cl_fcb_home26.png", "cl_fcb_0809.png"), "LA BLAUGRANA SE PRESUME"
    else:
        put(c, caps("EMPATE EN EL CAMP NOU", 34, NEON, 0.3), W / 2, 110)
        put(c, script("Nadie ganó,", 200, 5), W / 2 - 20, 250)
        put(c, script("todos presumen", 170, 5), W / 2 + 20, 430)
        trio, tag = ("rm125.png", "cl_fcb_home26.png", "cl_rm_away26.png"), "LA JERSEY SE PRESUME IGUAL"
    for n, dx, rot, y in zip(trio, (-0.3, 0, 0.3), (-9, 0, 9), (800, 770, 800)):
        jersey_glow(c, n, W / 2 + dx * W, y, 380, 400, rot)
    put(c, shop_box(tag, 34), W / 2, 1050)
    put(c, caps("3X2 EN FOOTBALLFRENZY.SHOP", 26, SOFT, 0.22), W / 2, 1130)
    sign(c, w=140, y=H - 80)
    return c


# ---------------------------------------------------------------- P5 combos 3x2

COMBOS = [
    ("Combo merengue", ("cl_rm_away26.png", "rm125.png", "cl_rm_third26.png"), "3 DEL MADRID"),
    ("Combo culé", ("barca_away.png", "cl_fcb_home26.png", "cl_fcb_third26.png"), "3 DEL BARÇA"),
    ("Casa dividida", ("rm125.png", "cl_fcb_home26.png", "cl_rm_1112.png"), "2 + 1 PARA LA FAMILIA"),
]


def p5_cover():
    c = base(0.36)
    put(c, caps("SEMANA DEL CLÁSICO", 30, NEON, 0.35), W / 2, 100)
    put(c, script("Arma tu", 200), W / 2 - 40, 240)
    put(c, neon(text("3X2", "Anton.ttf", 280, WHITE)), W / 2, 470)
    jersey_glow(c, "rm125.png", W * 0.3, 830, 400, 420, -8)
    jersey_glow(c, "cl_fcb_home26.png", W * 0.7, 830, 400, 420, 8)
    put(c, shop_box("LLEVA 3, PAGA 2", 42), W / 2, 1080)
    swipe(c, "ELIGE TU COMBO", 1165)
    sign(c, w=130, y=H - 72)
    return c


def p5_combo(i):
    title, trio, tag = COMBOS[i]
    c = base(0.32, 0.55)
    put(c, caps(f"OPCIÓN {i + 1}", 28, NEON, 0.35), W / 2, 95)
    put(c, script(title, 190 if len(title) < 14 else 170, 5), W / 2, 225)
    put(c, brush(640, 16, 60 + i), W / 2, 345, 1, 1, 3)
    for n, dx, rot, y in zip(trio, (-0.3, 0, 0.3), (-8, 0, 8), (690, 660, 690)):
        jersey_glow(c, n, W / 2 + dx * W, y, 380, 420, rot)
    put(c, neon(text("GRATIS", "Anton.ttf", 40, WHITE)), W / 2 + 0.3 * W, 920)
    put(c, shop_box(tag, 36), W / 2, 1020)
    put(c, rich((("PAGAS 2, ", WHITE), ("TE LLEVAS 3", NEON)), "Anton.ttf", 64), W / 2, 1125)
    sign(c, w=110, y=H - 58)
    return c


def p5_end():
    c = base(0.38)
    put(c, script("¿Cuál es tu combo?", 128, 5), W / 2, 230)
    put(c, text("Comenta 1, 2 o 3", "Inter-Bold.otf", 48, WHITE), W / 2, 400)
    put(c, brush(600, 16, 77), W / 2, 470, 1, 1, 2)
    put(c, text("El 3x2 se aplica solo en el carrito", "Inter-SemiBold.otf", 38, SOFT), W / 2, 560)
    put(c, text("y con el código 5X3 te llevas 5 y pagas 3", "Inter-SemiBold.otf", 38, SOFT), W / 2, 615)
    b2 = b.option(b.plane(72), "PÍDELA POR DM", "Te ayudamos con tallas y dorsal")
    b3 = b.option(b.globe(74), "FOOTBALLFRENZY.SHOP", "Envío gratis · Tallas S a 4XL")
    put(c, b2, W / 2, 790)
    put(c, b3, W / 2, 1000)
    sign(c, w=170, y=H - 110)
    return c


POSTS = {
    "p1-duelo": [p1_cover] + [lambda i=i: p1_round(i) for i in range(len(ROUNDS))] + [p1_end],
    "p2-retro": [p2_cover] + [lambda i=i: p2_slide(i) for i in range(len(RETRO))] + [p2_end],
    "p3-apuesta": [p3],
    "p4-dia-despues": [lambda: p4("madrid"), lambda: p4("barca"), lambda: p4("empate")],
    "p5-combos-3x2": [p5_cover] + [lambda i=i: p5_combo(i) for i in range(len(COMBOS))] + [p5_end],
}


if __name__ == "__main__":
    only = sys.argv[1:]
    for key, slides in POSTS.items():
        if only and not any(key.startswith(o) for o in only):
            continue
        d = OUT + key + "/"
        os.makedirs(d, exist_ok=True)
        for i, fn in enumerate(slides, 1):
            fn().convert("RGB").save(f"{d}{i:02d}.jpg", quality=93, subsampling=0)
        print(key, len(slides))
