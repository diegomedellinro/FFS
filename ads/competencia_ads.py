"""4 borradores de ads (feed 1080x1350) a partir del análisis de la competencia en Meta Ad Library (27 oct 2026).

A outfit   — "No es para el estadio. Es para la calle."  (lifestyle editorial; la competencia sólo muestra producto plano)
B precio   — "$533 por jersey"  (matemática clara contra 2x1 / 4x3 / 2x$999 de la competencia)
C versus   — "¿Retro o Spotify?"  (split con dos modelos, mezcla equipos en tu 3x2)
D regalo   — "El regalo que sí se va a poner"  (temporada navideña; Futbox ya usa el ángulo regalo con producto)
Uso: python3 competencia_ads.py
"""
import os
from PIL import Image, ImageDraw
import generar_ads as g
from generar_ads import put
from hf_ads import gradient
from barca_golf import serif, caps, lockup, ITAL
from carrusel_retro import fade, rule, GOLD, SOFT

RAW = g.HERE + "out/hf_ads/raw/"
OUT = g.HERE + "out/competencia/"
W, H = 1080, 1350
GOLF = RAW + "barca-golf-4k.png"
COLLAR = RAW + "rm-collar-4k.png"
RM = RAW + "retro-rm-4k.png"


def crop(src, w, h, y=0.0, x=0.5, zoom=1.0):
    """Cover-fit src into w x h; y/x pick the window (0..1), zoom > 1 crops tighter."""
    im = Image.open(src).convert("RGB")
    s = max(w / im.width, h / im.height) * zoom
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0 = int((im.width - w) * x)
    y0 = int((im.height - h) * y)
    return im.crop((x0, y0, x0 + w, y0 + h)).convert("RGBA")


def ad_outfit():
    c = crop(GOLF, W, H, y=0.10)
    gradient(c, top=True, h=0.22, k=0.5)
    fade(c, 930, 1060, 0.86)
    put(c, caps("BARÇA  ×  GOLF", 26, 0.45), W / 2, 60)
    put(c, serif("No es para el estadio.", 76), W / 2, 1075)
    put(c, serif("Es para la calle.", 64, ITAL, fill=SOFT), W / 2, 1160)
    put(c, caps("$800  ·  ARMA TU 3X2  ·  ENVÍO GRATIS", 24, 0.3, GOLD), W / 2, 1240)
    put(c, caps("FOOTBALLFRENZY.SHOP", 20, 0.3), W / 2, 1295)
    return c


def ad_precio():
    c = crop(COLLAR, W, H, y=0.16)
    gradient(c, top=True, h=0.3, k=0.55)
    fade(c, 900, 1030, 0.88)
    put(c, caps("LLEVA 3, PAGA 2", 26, 0.45), W / 2, 60)
    put(c, serif("$533", 230, track=0.01), W / 2, 1035)
    put(c, serif("por jersey. Sin códigos, sin letras chiquitas.", 40, ITAL, fill=SOFT), W / 2, 1165)
    put(c, rule(380), W / 2, 1215)
    put(c, caps("3 JERSEYS  ·  $1,600  ·  ENVÍO GRATIS", 24, 0.3, GOLD), W / 2, 1258)
    put(c, caps("FOOTBALLFRENZY.SHOP", 20, 0.3), W / 2, 1305)
    return c


def ad_versus():
    c = Image.new("RGBA", (W, H))
    half = W // 2
    c.alpha_composite(crop(RM, half, H, y=0.12, zoom=1.05), (0, 0))
    c.alpha_composite(crop(GOLF, half, H, y=0.10, zoom=1.05), (half, 0))
    ImageDraw.Draw(c).line([(half, 0), (half, H)], fill=(255, 255, 255, 230), width=4)
    gradient(c, top=True, h=0.22, k=0.55)
    fade(c, 960, 1080, 0.88)
    put(c, caps("RETRO", 28, 0.5), half / 2, 70)
    put(c, caps("SPOTIFY", 28, 0.5), half + half / 2, 70)
    put(c, serif("¿Retro o Spotify?", 88), W / 2, 1095)
    put(c, serif("¿Por qué no las dos? Mezcla equipos en tu 3x2.", 38, ITAL, fill=SOFT), W / 2, 1180)
    put(c, caps("3 POR $1,600  ·  FOOTBALLFRENZY.SHOP", 22, 0.3, GOLD), W / 2, 1260)
    return c


def ad_regalo():
    c = crop(RM, W, H, y=0.0)
    gradient(c, top=True, h=0.30, k=0.6)
    fade(c, 980, 1100, 0.88)
    put(c, caps("NAVIDAD 2026", 24, 0.45, GOLD), W / 2, 45)
    put(c, serif("El regalo que", 80), W / 2, 120)
    put(c, serif("sí se va a poner.", 60, ITAL), W / 2, 200)
    put(c, serif("Pide con tiempo: llega en 7 a 13 días hábiles.", 38, ITAL, fill=SOFT), W / 2, 1120)
    put(c, caps("3 POR $1,600  ·  ENVÍO GRATIS", 24, 0.3), W / 2, 1180)
    put(c, lockup(90), W / 2, 1270)
    return c


ADS = {"A-outfit": ad_outfit, "B-precio": ad_precio, "C-versus": ad_versus, "D-regalo": ad_regalo}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n, fn in ADS.items():
        fn().convert("RGB").save(f"{OUT}{n}.jpg", quality=93, subsampling=0)
    print("ok")
