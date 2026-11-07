"""Posts 'Idea de outfit' (1080x1350): jerseys reales de la tienda puestas en los flat-lays de outfit (él/ella)
con swap_jersey.py, sin IA de pago. Cada jersey va en la base cuyos colores combinan (verde/crema o denim/vino).

Uso: python3 ideas_outfit.py
"""
import os
import generar_ads as g
from generar_ads import put
from carrusel_outfits import club, sans, shadow, RAW
from swap_jersey import swap

OUT = g.HERE + "out/ideas_outfit/"
W, H = 1080, 1350

# (slug, base, recorte, título)
IDEAS = [
    ("rm-visitante-verde", "rm", "src/cl_rm_away26.png", ["REAL MADRID", "VISITANTE 26/27"]),
    ("portugal-2004", "fcb", "src/portugal/pt2004_cr7.png", ["PORTUGAL 2004"]),
    ("milan-0607", "fcb", "src/kaka.png", ["AC MILAN 06/07"]),
]


def post(slug, title_lines, n):
    c = club(slug, f"IDEA DE OUTFIT #{n}", title_lines)
    put(c, shadow(sans("3X2 EN JERSEYS · FOOTBALLFRENZY.SHOP", 26, track=0.08), 0.35), W / 2 - 60, H - 64)
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.chdir(g.HERE)
    for n, (slug, base, src, title) in enumerate(IDEAS, 1):
        swap(base, src, RAW + slug + ".png")
        post(slug, title, n).convert("RGB").save(f"{OUT}{n:02d}-{slug}.jpg", quality=93, subsampling=0)
    print("ok")
