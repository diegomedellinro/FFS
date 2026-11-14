"""Historia 5x3 'entre más jerseys, más descuento' (1080x1920), estilo de marca.
5 x $800 = $4,000 -> 5 por $2,400 (40% off). Escalera: 1 = $800 · 3 = $1,600 · 5 = $2,400.
Uso: python3 historia_5x3_escalera.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from buenfin_logo import jersey, shadow
from buenfin_2da50 import bg, red, white, pill, RED, GREY, WHITE

OUT = g.HERE + "out/historia_5x3/"
W, H = 1080, 1920
FIVE = [("cl_rm_third26.png", 0.84, 9), ("psg_home26.png", 0.92, 5), ("encargo/chivas.png", 1.0, 0),
        ("encargo/atlante.png", 0.92, -5), ("america110.png", 0.84, -9)]


def box(s, px):
    t = text(s, "Anton.ttf", px, RED, 0.03)
    b = Image.new("RGBA", (t.width + 56, t.height + 30), WHITE + (255,))
    b.alpha_composite(t, (28, 15))
    return shadow(b, 0.5, 10)


def ladder(y):
    """1 · 3 · 5 jerseys price steps."""
    c = Image.new("RGBA", (960, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    steps = [("1 JERSEY", "$800", ""), ("3 JERSEYS", "$1,600", "-33%"), ("5 JERSEYS", "$2,400", "-40%")]
    for i, (a, b, off) in enumerate(steps):
        x0 = i * 320
        hot = i == 2
        d.rounded_rectangle([x0 + 8, 6, x0 + 312, 214], radius=24, fill=(RED if hot else (22, 22, 26)) + (255,),
                            outline=(RED if not hot else WHITE) + (255,), width=3)
        ta = text(a, "MontB.ttf", 26, WHITE if hot else GREY, 0.08)
        tb = text(b, "Anton.ttf", 78, WHITE, 0.0)
        c.alpha_composite(ta, (x0 + 160 - ta.width // 2, 30))
        c.alpha_composite(tb, (x0 + 160 - tb.width // 2, 62))
        if off:
            to = text(off, "Anton.ttf", 30, WHITE if hot else RED, 0.02)
            c.alpha_composite(to, (x0 + 160 - to.width // 2, 165))
    return c


def story():
    c = bg(W, H)
    put(c, badge(140), W / 2, 150)
    put(c, white("ENTRE MÁS JERSEYS AGREGUES AL CARRITO,", 36, 0.02, "MontB.ttf"), W / 2, 290)
    put(c, white("MÁS DESCUENTO OBTIENES.", 36, 0.02, "MontB.ttf"), W / 2, 345)
    put(c, box("HASTA 40% OFF EN EL BUEN FIN", 54), W / 2, 440)
    put(c, text("ANTES $4,000", "MontB.ttf", 70, (95, 95, 102), 0.0, strike=(150, 150, 158)), W / 2 - 150, 590)
    put(c, white("5 JERSEYS POR", 62, 0.02), W / 2 + 250, 680)
    put(c, red("$2,400", 290, 0.0), W / 2, 900)
    xs = [W / 2 + k * 172 for k in (-2, -1, 0, 1, 2)]
    for i in (0, 4, 1, 3, 2):
        n, k, r = FIVE[i]
        put(c, jersey(n, int(390 * k), r), xs[i], 1290 + (1 - k) * 150)
    put(c, ladder(0), W / 2, 1625)
    put(c, pill("5x3 AUTOMÁTICO EN EL CARRITO · ENVÍO GRATIS", 40), W / 2, 1790)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    story().convert("RGB").save(OUT + "story-5x3-entre-mas.jpg", quality=94, subsampling=0)
    print("ok")
