"""Anuncios de venta Real Madrid (post-Clásico) para Meta, destino footballfrenzy.shop/collections/real-madrid.

Conceptos:
  A blanco   — "El Clásico es blanco": visitante 26/27 de héroe + 125 aniversario y tercera.
  B trio     — "Las 3 del Madrid por $1,600": blanca, verde y rosa con precio por pieza.
  C retro    — "Leyendas blancas": retro 09/10, 11/12, 17/18 también en 3x2.
  D prueba   — foto real de cliente con jersey del Madrid + "así llega tu pedido".
Tamaños: feed 1080x1350 y historia 1080x1920 (texto clave dentro de la zona segura).
Video: A en 1080x1920, 10 s.
Uso: python3 rm_ads.py [--video]
"""
import math, os, sys, subprocess
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import text, rich, put, ease, back, WHITE, INK, GREY
from abre_la_foto import NEON, neon, jersey_glow, shop_box, caps, logo

OUT = g.HERE + "out/rm_ads/"
SOFT = (205, 205, 210)
GREEN = (0, 120, 80)


class L:
    """Layout for feed (1080x1350) or story (1080x1920): y(k) maps 0..1 into the safe band."""
    def __init__(self, H):
        self.W, self.H = 1080, H
        self.story = H > 1500
        self.top = 250 if self.story else 60
        self.bot = 1540 if self.story else 1300

    def y(self, k):
        return self.top + (self.bot - self.top) * k


def bg(l, glows=((0.5, 0.5, 0.75, (150, 10, 20), 0.34),)):
    return g.background(l.W, l.H, glows, base=(6, 6, 7)).copy()


def headline(s, px, color=WHITE):
    return neon(text(s, "Anton.ttf", px, color, 0.01), r=(8, 22), k=(0.9, 0.6), drop=(4, 6))


def price_bar(l, c, y, a=1.0):
    put(c, rich((("3 JERSEYS POR ", WHITE), ("$1,600", NEON)), "Anton.ttf", 78), l.W / 2, y, a)
    put(c, caps("LLEVA 3, PAGA 2  ·  ENVÍO GRATIS  ·  TALLAS S A 4XL", 24, SOFT, 0.14), l.W / 2, y + 70, a)


def cta(l, c, y, a=1.0, label="COMPRA EN FOOTBALLFRENZY.SHOP"):
    put(c, g.cta(label, 900, 40), l.W / 2, y, a)


def brand(l, c, y=None):
    put(c, logo(150 if l.story else 120), l.W / 2, y if y else (l.top + 55 if l.story else 75))


def P(l):
    """Fixed vertical slots per format (story keeps everything inside y 250-1540)."""
    if l.story:
        return dict(logo=300, kick=410, h1=520, h2=670, jy=1010, strip=1250, price=1335, cta=1500)
    return dict(logo=72, kick=150, h1=240, h2=380, jy=665, strip=915, price=1020, cta=1250)


# ---------------------------------------------------------------- A: El Clásico es blanco

def blanco(H, t=99):
    l = L(H); p = P(l)
    c = bg(l, ((0.5, 0.55, 0.8, (150, 10, 20), 0.36), (0.5, 0.4, 0.35, (255, 255, 255), 0.06)))
    put(c, logo(140 if l.story else 110), l.W / 2, p["logo"])
    a1, a1b, a2, a3 = back(t, 0.2, 0.55), back(t, 0.35, 0.55), ease(t, 0.6), ease(t, 1.0)
    put(c, caps("REAL MADRID", 30, NEON, 0.45), l.W / 2, p["kick"], ease(t, 0.0))
    put(c, headline("EL CLÁSICO", 140), l.W / 2, p["h1"], min(1, a1), 0.85 + 0.15 * min(1, a1))
    put(c, headline("ES BLANCO", 140), l.W / 2, p["h2"], min(1, a1b), 0.85 + 0.15 * min(1, a1b))
    jy = p["jy"]
    if a2 > 0.01:
        jersey_glow(c, "rm125.png", l.W * 0.2 - (1 - a2) * 200, jy + 30, 360, 380, -10)
        jersey_glow(c, "cl_rm_third26.png", l.W * 0.8 + (1 - a2) * 200, jy + 30, 360, 380, 10)
    k = back(t, 0.45, 0.6)
    if k > 0.01:
        jersey_glow(c, "cl_rm_away26.png", l.W / 2, jy - (1 - min(1, k)) * 80, 480, 480, 0)
    put(c, shop_box("NUEVA VISITANTE 26/27", 30), l.W / 2, p["strip"], a2)
    price_bar(l, c, p["price"], a3)
    cta(l, c, p["cta"], ease(t, 1.3))
    return c


# ---------------------------------------------------------------- B: las 3 por $1,600

def trio(H, t=99):
    l = L(H); p = P(l)
    c = bg(l)
    put(c, logo(140 if l.story else 110), l.W / 2, p["logo"])
    put(c, caps("REAL MADRID 26/27", 30, NEON, 0.45), l.W / 2, p["kick"])
    put(c, headline("LAS 3 DEL MADRID", 112), l.W / 2, p["h1"])
    put(c, rich((("POR ", WHITE), ("$1,600", NEON)), "Anton.ttf", 140), l.W / 2, p["h2"])
    jy = p["jy"] - 30
    items = (("rm125.png", "LA BLANCA", "125 aniversario"), ("cl_rm_away26.png", "LA VERDE", "Visitante 26/27"), ("cl_rm_third26.png", "LA ROSA", "Tercera 26/27"))
    for i, (n, name, sub) in enumerate(items):
        x = l.W * (0.19 + 0.31 * i)
        jersey_glow(c, n, x, jy, 320, 340, (-6, 0, 6)[i])
        put(c, caps(name, 28, WHITE, 0.2), x, jy + 200)
        put(c, text(sub, "Inter-SemiBold.otf", 24, SOFT), x, jy + 238)
    put(c, shop_box("SALEN EN $533 CADA UNA", 34), l.W / 2, p["price"])
    put(c, caps("3X2 AUTOMÁTICO EN EL CARRITO  ·  ENVÍO GRATIS", 24, SOFT, 0.14), l.W / 2, p["price"] + 72)
    cta(l, c, p["cta"], label="ARMA TU 3X2 EN FOOTBALLFRENZY.SHOP")
    return c


# ---------------------------------------------------------------- C: leyendas blancas (retro)

def retro(H, t=99):
    l = L(H); p = P(l)
    c = bg(l, ((0.5, 0.55, 0.8, (150, 10, 20), 0.3), (0.5, 0.2, 0.5, (120, 90, 20), 0.12)))
    put(c, logo(140 if l.story else 110), l.W / 2, p["logo"])
    put(c, caps("REAL MADRID RETRO", 30, NEON, 0.45), l.W / 2, p["kick"])
    put(c, headline("LEYENDAS", 140), l.W / 2, p["h1"])
    put(c, headline("BLANCAS", 140), l.W / 2, p["h2"])
    jy = p["jy"] - 20
    items = (("cl_rm_0910.png", "09/10"), ("cl_rm_1112.png", "11/12"), ("cl_rm_1718ls.png", "17/18"))
    for i, (n, yr) in enumerate(items):
        x = l.W * (0.19 + 0.31 * i)
        jersey_glow(c, n, x, jy, 330, 360, (-6, 0, 6)[i])
        put(c, neon(text(yr, "Anton.ttf", 60, WHITE)), x, jy + 225)
    price_bar(l, c, p["price"])
    cta(l, c, p["cta"])
    return c


# ---------------------------------------------------------------- D: prueba social (foto real)

def prueba(H, t=99):
    l = L(H); p = P(l)
    c = bg(l)
    put(c, logo(140 if l.story else 110), l.W / 2, p["logo"])
    put(c, caps("FOTO REAL DE CLIENTE", 30, NEON, 0.45), l.W / 2, p["kick"])
    put(c, headline("ASÍ LLEGA TU JERSEY", 104), l.W / 2, p["h1"] - 10)
    py = p["jy"] - 60
    ph = Image.open(g.SRC + "review_201928.jpg").convert("RGB")
    w, h = (520, 560) if l.story else (470, 480)
    s = max(w / ph.width, h / ph.height)
    ph = ph.resize((round(ph.width * s), round(ph.height * s)), Image.LANCZOS)
    ph = ph.crop(((ph.width - w) // 2, (ph.height - h) // 2, (ph.width - w) // 2 + w, (ph.height - h) // 2 + h))
    card = Image.new("RGBA", (w + 24, h + 24), (255, 255, 255, 255))
    card.paste(ph, (12, 12))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=28, fill=255)
    card.putalpha(m)
    put(c, neon(card, r=(10, 30), k=(0.7, 0.5), drop=(0, 0)), l.W / 2 - 110, py, 1, 1, -4)
    jersey_glow(c, "cl_rm_away26.png", l.W / 2 + 280, py + 130, 300, 310, 8)
    put(c, rich((("+3,000 ", NEON), ("PEDIDOS ENTREGADOS", WHITE)), "Anton.ttf", 64), l.W / 2, p["price"])
    put(c, caps("RASTREO EN CADA PEDIDO  ·  ENVÍO GRATIS  ·  3X2", 24, SOFT, 0.14), l.W / 2, p["price"] + 70)
    cta(l, c, p["cta"])
    return c


CONCEPTS = {"A-blanco": blanco, "B-trio": trio, "C-retro": retro, "D-prueba": prueba}


def video(fn, H, dur=10, path=None):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"1080x{H}", "-r", "30",
           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(dur * 30):
        p.stdin.write(fn(H, i / 30).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in CONCEPTS.items():
        for H, tag in ((1350, "feed"), (1920, "historia")):
            fn(H).convert("RGB").save(f"{OUT}{name}-{tag}.jpg", quality=93, subsampling=0)
        print(name)
    if "--video" in sys.argv:
        video(blanco, 1920, 10, OUT + "A-blanco-video-1080x1920.mp4")
        video(blanco, 1350, 10, OUT + "A-blanco-video-1080x1350.mp4")
        print("video")
