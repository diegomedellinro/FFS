"""Carrusel 'Barça x artistas de Spotify' (1080x1350), misma estética editorial que el carrusel retro.

Portada (foto Barça x Golf) → 5 ediciones especiales que vende la tienda → cómo funciona el 3x2 → cierre con CTA.
Uso: python3 carrusel_spotify.py
"""
import os
from PIL import Image, ImageFilter
import generar_ads as g
from generar_ads import put
from hf_ads import gradient
from barca_golf import serif, caps, ITAL
import carrusel_retro as cr
from carrusel_retro import W, H, SOFT, GOLD, fade, jersey, rule, counter

OUT = g.HERE + "out/carrusel_spotify/"
cr.PHOTO = g.HERE + "out/hf_ads/raw/barca-outpaint-4k.png"  # foto del cliente ampliada + upscale 4K

JERSEYS = [
    ("spotify/golf.png", "TYLER, THE CREATOR", "GOLF", "El logo de Golf Wang en el pecho"),
    ("spotify/sheeran.png", "ED SHEERAN", "PLAY", "Su álbum de 2025 en la camiseta"),
    ("spotify/travis_fan.png", "TRAVIS SCOTT", "CACTUS JACK", "Edición local"),
    ("spotify/travis_2425.png", "TRAVIS SCOTT", "CACTUS JACK", "Edición visitante en negro"),
    ("spotify/travis_skel.png", "TRAVIS SCOTT  ·  RETRO 2000/01", "SKELETON", "La local 2000/01, reinterpretada"),
]


def halo(lay, k=0.35):
    """Soft light glow behind dark jerseys so they read on the dark backdrop."""
    a = lay.getchannel("A").filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * k))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(Image.composite(Image.new("RGBA", lay.size, (190, 190, 205, 255)), out.copy(), a))
    out.alpha_composite(lay)
    return out


def cover():
    c = cr.base(W, H, 0.03, cr.PHOTO)
    gradient(c, top=True, h=0.32, k=0.6)
    put(c, caps("3X2 ACTIVO", 26, 0.45), W / 2, 70)
    put(c, serif("BARÇA", 150, track=0.02), W / 2, 175)
    put(c, serif("x los artistas de Spotify", 56, ITAL), W / 2, 285)
    fade(c, 1020, 1130, 0.82)
    put(c, serif("Cuando el patrocinio se vuelve un artista", 42, ITAL), W / 2, 1170)
    put(c, caps("DESLIZA  >>", 24, 0.4), W / 2, 1250)
    return c


def slide(i, name, kick, title, line):
    c = cr.backdrop()
    put(c, caps(kick, 26, 0.45, GOLD), W / 2, 110)
    put(c, serif(title, 120 if len(title) < 9 else 104, track=0.02), W / 2, 205)
    put(c, serif(line, 44, ITAL, fill=SOFT), W / 2, 305)
    lay = jersey(name, 690)
    if "2425" in name:
        lay = halo(lay)
    put(c, lay, W / 2, 750)
    put(c, rule(420), W / 2, 1160)
    put(c, caps("$800  ·  3 POR $1,600", 30, 0.3), W / 2, 1215)
    counter(c, i, 5)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slides = [cover] + [lambda i=i, j=j: slide(i, *j) for i, j in enumerate(JERSEYS, 1)] + [cr.como, cr.cierre]
    for n, fn in enumerate(slides, 1):
        fn().convert("RGB").save(f"{OUT}{n:02d}.jpg", quality=93, subsampling=0)
    print(len(slides), "slides")
