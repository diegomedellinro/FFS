"""Carrusel 'Cómo combinar tu jersey' (1080x1350), formato outfit-grid: fondo gris concreto, "HOME KIT" + nombre del club,
dos outfits (él / ella). Madrid y Barça generados con Higgsfield; América, Inter Miami y PSG hechos con swap_jersey.py
(misma ropa, jersey real de la tienda pegada encima), sin costo.

Portada → un slide por club (out/outfits/raw/<club>.png) → cierre con CTA.
Uso: python3 carrusel_outfits.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter
import generar_ads as g
from generar_ads import put, text
from hf_ads import badge
from competencia_ads import crop

RAW = g.HERE + "out/outfits/raw/"
OUT = g.HERE + "out/outfits/"
W, H = 1080, 1350
WHITE, INK, RED = (255, 255, 255), (20, 20, 22), (225, 30, 45)

CLUBS = [
    ("real-madrid", "HOME KIT", ["REAL MADRID"]),
    ("barca-golf", "EDICIÓN GOLF", ["FC BARCELONA"]),
    ("america", "HOME KIT", ["CLUB AMÉRICA"]),
    ("inter-miami", "HOME KIT", ["INTER MIAMI"]),
    ("psg", "HOME KIT", ["PARIS", "SAINT-GERMAIN"]),
]


def sans(s, px, fill=WHITE, track=0.0):
    return text(s, "MontB.ttf", int(px), fill, track)


def shadow(lay, k=0.25):
    """Very soft shadow so white type reads on light grey."""
    out = Image.new("RGBA", (lay.width + 40, lay.height + 40), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(lay.getchannel("A"), (20, 24))
    a = a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * k))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(lay, (20, 20))
    return out


def concrete():
    """Light grey concrete texture like the outfit-grid backgrounds."""
    rng = np.random.default_rng(7)
    n = rng.normal(0, 1, (H // 4, W // 4))
    n = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32)
    fine = rng.normal(0, 6, (H, W))
    yy = np.linspace(0, 1, H)[:, None]
    base = 178 - 14 * yy + (n - 128) * 0.06 + fine
    rgb = np.dstack([base, base + 1, base + 3]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgb).convert("RGBA")


def title(c, kicker, lines, y=130):
    put(c, shadow(sans(kicker, 40, track=0.04)), W / 2, y)
    for i, s in enumerate(lines):
        put(c, shadow(sans(s, 118 if len(s) < 12 else 100, track=0.01)), W / 2, y + 115 + i * 120)


def mark(c):
    put(c, badge(110), W / 2, H - 78)


def club(slug, kicker, lines, k=0.8):
    """Outfit image scaled down to the lower part; its own blurred texture fills the frame so the title has room."""
    im = crop(RAW + slug + ".png", W, H)
    edge = np.concatenate([np.asarray(im.convert("RGB"))[:60].reshape(-1, 3), np.asarray(im.convert("RGB"))[:, :40].reshape(-1, 3)])
    tex = np.asarray(concrete().convert("RGB"), np.float32)
    tex = tex - tex.reshape(-1, 3).mean(0) + np.median(edge, 0)
    bg = Image.fromarray(tex.clip(0, 255).astype(np.uint8)).convert("RGBA")
    w, h = int(W * k), int(H * k)
    im = im.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0)
    m.paste(255, (60, 60, w - 60, h - 60))
    m = m.filter(ImageFilter.GaussianBlur(45))
    bg.paste(im, ((W - w) // 2, H - h - 10), m)
    title(bg, kicker, lines, y=75)
    put(bg, badge(84), W - 70, H - 64)
    return bg


def cover():
    c = concrete()
    put(c, shadow(sans("OUTFITS", 44, track=0.3)), W / 2, 330)
    put(c, shadow(sans("¿CÓMO COMBINAR", 92)), W / 2, 470)
    put(c, shadow(sans("TU JERSEY?", 140)), W / 2, 615)
    put(c, sans("PARA ÉL Y PARA ELLA", 40, INK, 0.18), W / 2, 790)
    put(c, sans("DESLIZA  >>", 32, RED, 0.3), W / 2, 900)
    put(c, badge(170), W / 2, 1140)
    return c


def cierre():
    c = concrete()
    put(c, shadow(sans("3X2 EN TODAS", 112)), W / 2, 380)
    put(c, shadow(sans("LAS JERSEYS", 112)), W / 2, 505)
    put(c, sans("3 POR $1,600  ·  ENVÍO GRATIS", 44, INK, 0.08), W / 2, 650)
    put(c, sans("HAZ TU PEDIDO POR MENSAJE DIRECTO", 34, INK, 0.06), W / 2, 790)
    put(c, sans("O EN FOOTBALLFRENZY.SHOP", 34, RED, 0.06), W / 2, 845)
    put(c, badge(200), W / 2, 1110)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [cover] + [lambda a=a: club(*a) for a in CLUBS if os.path.exists(RAW + a[0] + ".png")] + [cierre]
    for n, fn in enumerate(slides, 1):
        fn().convert("RGB").save(f"{OUT}{n:02d}.jpg", quality=93, subsampling=0)
    print(len(slides), "slides")
