"""3 creativos FB (1080x1350) con fotos Higgsfield (GPT Image 2.5, jerseys reales de la tienda como referencia).

1 rivales  — Madrid local 26/27 + Barça x Golf: "Rivales en la cancha. Mismo carrito."
2 unboxing — "Tu 3x2, en tu puerta." (confianza: envío gratis, rastreo, pago con tarjeta)
3 rack     — "$533 por jersey" (precio por pieza, temporada 26/27)
Uso: python3 fb3_ads.py
"""
import os
import generar_ads as g
from generar_ads import put
from hf_ads import gradient
from barca_golf import serif, caps, lockup, ITAL
from carrusel_retro import fade, rule, GOLD, SOFT
from competencia_ads import crop

RAW = g.HERE + "out/fb3/raw/"
OUT = g.HERE + "out/fb3/"
W, H = 1080, 1350


def rivales():
    c = crop(RAW + "1-rivales.png", W, H)
    gradient(c, top=True, h=0.3, k=0.6)
    fade(c, 1010, 1120, 0.85)
    put(c, caps("REAL MADRID  ×  FC BARCELONA", 24, 0.4, GOLD), W / 2, 55)
    put(c, serif("Rivales en la cancha.", 76), W / 2, 135)
    put(c, serif("Mismo carrito.", 64, ITAL), W / 2, 215)
    put(c, caps("3 JERSEYS POR $1,600  ·  ENVÍO GRATIS", 26, 0.28), W / 2, 1160)
    put(c, lockup(96), W / 2, 1262)
    return c


def unboxing():
    c = crop(RAW + "2-unboxing.png", W, H)
    gradient(c, top=True, h=0.32, k=0.7)
    fade(c, 1040, 1140, 0.85)
    put(c, caps("ASÍ LLEGA TU PEDIDO", 24, 0.45, GOLD), W / 2, 55)
    put(c, serif("Tu 3x2,", 92), W / 2, 140)
    put(c, serif("en tu puerta.", 70, ITAL), W / 2, 232)
    put(c, caps("ENVÍO GRATIS  ·  RASTREO  ·  PAGO CON TARJETA", 22, 0.25), W / 2, 1180)
    put(c, lockup(90), W / 2, 1270)
    return c


def rack():
    c = crop(RAW + "3-rack.png", W, H)
    gradient(c, top=True, h=0.26, k=0.55)
    fade(c, 980, 1090, 0.88)
    put(c, caps("TEMPORADA 26/27  ·  LLEVA 3, PAGA 2", 24, 0.4, GOLD), W / 2, 60)
    put(c, serif("$533", 200), W / 2, 1050)
    put(c, serif("por jersey. Madrid, Barça o los dos.", 40, ITAL, fill=SOFT), W / 2, 1165)
    put(c, rule(380), W / 2, 1210)
    put(c, caps("FOOTBALLFRENZY.SHOP  ·  ENVÍO GRATIS", 22, 0.3), W / 2, 1260)
    return c


ADS = {"1-rivales": rivales, "2-unboxing": unboxing, "3-precio": rack}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n, fn in ADS.items():
        fn().convert("RGB").save(f"{OUT}{n}.jpg", quality=93, subsampling=0)
    print("ok")
