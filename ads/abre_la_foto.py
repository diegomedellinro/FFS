"""Carrusel trend "ABRE LA FOTO": mensaje de foto de una sola vista → me debes una jersey para el clásico → pídela.

Formato 1080x1350 (4:5). Uso: python3 abre_la_foto.py
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import text, rich, pill, put, WHITE, RED, INK, GREY

W, H = 1080, 1350
OUT = g.HERE + "out/abre_la_foto/"
TREND_RED = (196, 28, 36)
WA_GREEN = (37, 160, 90)


def bubble(scale=1.0):
    """WhatsApp-style 'view once' photo message: ①  Foto   10:37."""
    s = scale
    w, h, tail = int(560 * s), int(200 * s), int(46 * s)
    im = Image.new("RGBA", (w + tail + 40, h + 60), (0, 0, 0, 0))
    ox, oy = tail, 10
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([ox, oy + 12, ox + w, oy + h + 12], radius=int(52 * s), fill=110)
    im.putalpha(sh.filter(ImageFilter.GaussianBlur(18)))
    im = Image.composite(Image.new("RGBA", im.size, (0, 0, 0, 255)), Image.new("RGBA", im.size, (0, 0, 0, 0)), im.getchannel("A"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([ox, oy, ox + w, oy + h], radius=int(52 * s), fill=(255, 255, 255, 255))
    # tail at bottom-left
    d.polygon([(ox + 40 * s, oy + h - 70 * s), (ox - tail * 0.8, oy + h + 6 * s), (ox + 100 * s, oy + h - 8 * s)], fill=(255, 255, 255, 255))
    # view-once icon: dashed green ring with a 1
    cx, cy, r = ox + 110 * s, oy + h * 0.44, 42 * s
    lw = max(4, int(7 * s))
    d.arc([cx - r, cy - r, cx + r, cy + r], -60, 200, fill=WA_GREEN, width=lw)
    for st in (214, 240, 266):  # dashed segment on the upper-left
        d.arc([cx - r, cy - r, cx + r, cy + r], st, st + 12, fill=WA_GREEN, width=lw)
    one = text("1", "Inter-SemiBold.otf", int(46 * s), WA_GREEN)
    im.alpha_composite(one, (int(cx - one.width / 2), int(cy - one.height / 2)))
    foto = text("Foto", "Inter-SemiBold.otf", int(70 * s), (30, 30, 34))
    im.alpha_composite(foto, (int(cx + r + 34 * s), int(cy - foto.height / 2)))
    hr = text("10:37", "Inter-SemiBold.otf", int(44 * s), (110, 110, 116))
    im.alpha_composite(hr, (int(ox + w - hr.width - 34 * s), int(oy + h - hr.height - 18 * s)))
    return im


def footer(c):
    put(c, g.brand(24), W / 2, H - 60)


def slide1():
    c = Image.new("RGBA", (W, H), TREND_RED + (255,))
    c.alpha_composite(g.background(W, H, ((0.5, 0.4, 0.8, (226, 40, 46), 0.5),), base=TREND_RED).copy())
    put(c, text("ABRE", "Anton.ttf", 250, WHITE, 0.0), W / 2, 330)
    put(c, text("LA FOTO", "Anton.ttf", 250, WHITE, 0.0), W / 2, 590)
    put(c, bubble(1.0), W / 2 - 10, 930)
    footer(c)
    return c


def slide2():
    c = g.background(W, H, ((0.27, 0.62, 0.42, (240, 240, 245), 0.22), (0.73, 0.62, 0.42, (160, 30, 70), 0.45))).copy()
    c.alpha_composite(g.stripes(W, H, alpha=8))
    put(c, text("ME DEBES UNA JERSEY", "Anton.ttf", 108, WHITE, 0.01), W / 2, 150)
    put(c, rich((("PARA EL ", WHITE), ("CLÁSICO", RED)), "Anton.ttf", 150), W / 2, 285)
    g.product(c, "rm125.png", W * 0.28, 720, 520, 600, 1, 1, -6)
    g.product(c, "barca_away.png", W * 0.72, 740, 520, 600, 1, 1, 6)
    put(c, text("VS", "Anton.ttf", 110, WHITE), W / 2, 700)
    for x, s in ((W * 0.28, "REAL MADRID"), (W * 0.72, "BARÇA")):
        put(c, pill(s, "Anton.ttf", 40, WHITE, INK, track=0.05), x, 1060)
    put(c, text("Etiqueta a quien te la debe", "Inter-Bold.otf", 46, WHITE), W / 2, 1175)
    footer(c)
    return c


def plane(px, color=WHITE):
    """Instagram-style DM paper plane outline."""
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(4, px // 12)
    a, b, cc = (px * 0.08, px * 0.12), (px * 0.92, px * 0.12), (px * 0.55, px * 0.9)
    d.line([a, b, cc, (px * 0.42, px * 0.42), a], fill=color, width=lw, joint="curve")
    d.line([(px * 0.42, px * 0.42), b], fill=color, width=lw)
    return im


def option(icon, title, sub, w=880, h=190):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=40, fill=(255, 255, 255, 255))
    d.ellipse([34, h / 2 - 60, 154, h / 2 + 60], fill=RED)
    im.alpha_composite(icon, (int(94 - icon.width / 2), int(h / 2 - icon.height / 2)))
    t1 = text(title, "Anton.ttf", 64, INK, 0.01)
    t2 = text(sub, "Inter-SemiBold.otf", 34, (100, 100, 106))
    im.alpha_composite(t1, (190, int(h / 2 - t1.height + 2)))
    im.alpha_composite(t2, (192, int(h / 2 + 8)))
    return im


def globe(px, color=WHITE):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(4, px // 14)
    m = lw
    d.ellipse([m, m, px - m, px - m], outline=color, width=lw)
    d.ellipse([px * 0.3, m, px * 0.7, px - m], outline=color, width=lw)
    d.line([(m, px / 2), (px - m, px / 2)], fill=color, width=lw)
    return im


def slide3():
    c = Image.new("RGBA", (W, H), TREND_RED + (255,))
    c.alpha_composite(g.background(W, H, ((0.5, 0.45, 0.8, (226, 40, 46), 0.5),), base=TREND_RED).copy())
    put(c, text("PÍDELA", "Anton.ttf", 210, WHITE), W / 2, 230)
    put(c, text("ANTES DEL CLÁSICO", "Anton.ttf", 92, WHITE, 0.02), W / 2, 395)
    put(c, option(plane(64), "POR MENSAJE DIRECTO", "Escríbenos por DM y te ayudamos"), W / 2, 590)
    put(c, text("o", "Inter-Bold.otf", 48, WHITE), W / 2, 725)
    put(c, option(globe(66), "EN FOOTBALLFRENZY.SHOP", "Elige talla, versión y dorsal"), W / 2, 860)
    put(c, rich((("LLEVA 3, ", WHITE), ("PAGA 2", INK)), "Anton.ttf", 84), W / 2, 1060)
    put(c, g.checks(("Envío gratis", "Tallas S a 4XL", "Pago seguro"), 30, WHITE, INK), W / 2, 1150)
    footer(c)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i, fn in enumerate((slide1, slide2, slide3), 1):
        fn().convert("RGB").save(f"{OUT}{i}-{fn.__name__}.jpg", quality=93, subsampling=0)
    print("ok")
