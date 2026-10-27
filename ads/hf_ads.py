"""Anuncios fotorrealistas (Higgsfield, GPT Image 2.5 + upscale 4K) con tipografía y logo de Football Frenzy encima.

Fotos 4:5 en out/hf_ads/raw/*-4k.png  ->  out/hf_ads/NN-nombre.jpg (4K, 3456x4320 aprox).
Videos 9:16 en out/hf_ads/raw/vN.mp4   ->  out/hf_ads/video-N.mp4 (hook + CTA final), con --video.
El modelo es una persona generada por IA (no es la persona de la foto de inspiración).
Uso: python3 hf_ads.py [--video]
"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import generar_ads as g
from generar_ads import text, put
from abre_la_foto import NEON

RAW = g.HERE + "out/hf_ads/raw/"
OUT = g.HERE + "out/hf_ads/"
WHITE, INK, SOFT = (255, 255, 255), (10, 10, 11), (225, 225, 230)


def badge(d):
    """Real logo inside a black circle (works on light and dark photos)."""
    lg = Image.open(g.SRC + "logo_ff.png").convert("RGB").resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d - 1, d - 1], fill=255)
    out = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    out.paste(lg, (0, 0), m)
    sh = Image.new("RGBA", (int(d * 1.3), int(d * 1.3)), (0, 0, 0, 0))
    a = Image.new("L", sh.size, 0)
    ImageDraw.Draw(a).ellipse([d * .15, d * .17, d * 1.15, d * 1.17], fill=120)
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(d * .05)))
    sh.alpha_composite(out, (int(d * .15), int(d * .15)))
    return sh


def shadowed(layer, k=0.45, r=None):
    """Soft drop shadow so white type survives on light backgrounds."""
    r = r or max(6, layer.height // 14)
    p = r * 3
    out = Image.new("RGBA", (layer.width + 2 * p, layer.height + 2 * p), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(layer.getchannel("A"), (p, p + r // 2))
    a = a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * k))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), a))
    out.alpha_composite(layer, (p, p))
    return out


def H(s, px, color=WHITE, track=0.0):
    return text(s, "Anton.ttf", int(px), color, track)


def caps(s, px, color=WHITE, track=0.18):
    return text(s, "MontB.ttf", int(px), color, track)


def pill(s, px, fg=WHITE, line=WHITE):
    t = caps(s, px, fg, 0.06)
    w, h = int(t.width + px * 1.6), int(t.height + px * 0.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([1, 1, w - 2, h - 2], radius=h // 2, outline=line + (255,), width=max(2, int(px * .09)))
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return im


def gradient(c, top=True, h=0.35, k=0.65):
    """Dark fade at top or bottom for type legibility."""
    W, Hh = c.size
    g_ = np.zeros((Hh, W), np.float32)
    n = int(Hh * h)
    ramp = np.linspace(k, 0, n) ** 1.6
    if top:
        g_[:n] = ramp[:, None]
    else:
        g_[Hh - n:] = ramp[::-1][:, None]
    a = Image.fromarray((g_ * 255).astype(np.uint8))
    c.alpha_composite(Image.composite(Image.new("RGBA", c.size, (0, 0, 0, 255)), Image.new("RGBA", c.size, (0, 0, 0, 0)), a))


def load(name):
    return Image.open(RAW + name).convert("RGBA")


# ------------------------------------------------------------------ 5 fotos

def p1_hero():
    """'You can't win. So win.' -> No viniste a ver. Viniste a ganar."""
    c = load("01-hero-4k.png"); W, Hh = c.size; u = W / 1080
    put(c, shadowed(H("NO VINISTE A VER.", 112 * u)), W / 2, 150 * u)
    put(c, shadowed(H("VINISTE A GANAR.", 150 * u), 0.35), W / 2, 780 * u)
    gradient(c, top=False, h=0.22, k=0.55)
    put(c, badge(int(150 * u)), 120 * u, Hh - 120 * u)
    put(c, caps("JERSEYS 3 POR $1,600", 30 * u, WHITE, 0.2), W - 300 * u, Hh - 140 * u)
    put(c, caps("FOOTBALLFRENZY.SHOP", 26 * u, SOFT, 0.22), W - 300 * u, Hh - 92 * u)
    return c


def p2_trio():
    c = load("02-trio-4k.png"); W, Hh = c.size; u = W / 1080
    gradient(c, top=True, h=0.18, k=0.5)
    gradient(c, top=False, h=0.32, k=0.8)
    put(c, badge(int(150 * u)), W / 2, Hh - 420 * u)
    put(c, H("LLEVA 3. PAGA 2.", 150 * u), W / 2, Hh - 250 * u)
    put(c, caps("COMPRA EN FOOTBALLFRENZY.SHOP", 30 * u, WHITE, 0.3), W / 2, Hh - 110 * u)
    return c


def p3_silla():
    c = load("03-silla-4k.png"); W, Hh = c.size; u = W / 1080
    put(c, pill("NUEVA TEMPORADA", 24 * u), 200 * u, 80 * u)
    put(c, caps("FOOTBALL FRENZY SHOP", 24 * u, SOFT, 0.2), W - 250 * u, 80 * u)
    gradient(c, top=False, h=0.3, k=0.7)
    put(c, H("TU JERSEY NO SE PRESTA.", 104 * u), W / 2, Hh - 250 * u)
    put(c, text("Envío gratis a todo México · 3x2 automático en el carrito", "Inter-SemiBold.otf", int(32 * u), SOFT), W / 2, Hh - 150 * u)
    put(c, caps("FOOTBALLFRENZY.SHOP", 26 * u, NEON, 0.3), W / 2, Hh - 85 * u)
    return c


def p4_tacos():
    c = load("04-taquetes-4k.png"); W, Hh = c.size; u = W / 1080
    put(c, pill("EDICIÓN ESPECIAL", 24 * u), 190 * u, 80 * u)
    put(c, caps("DISPONIBLE YA", 24 * u, SOFT, 0.2), W - 170 * u, 80 * u)
    put(c, badge(int(150 * u)), W / 2, Hh - 470 * u)
    put(c, H("TACOS QUE SE VEN", 112 * u), W / 2, Hh - 300 * u)
    put(c, H("DESDE LA TRIBUNA.", 112 * u), W / 2, Hh - 175 * u)
    put(c, text("Pídelos en footballfrenzy.shop · Envío gratis", "Inter-SemiBold.otf", int(32 * u), SOFT), W / 2, Hh - 80 * u)
    return c


def p5_retro():
    c = load("05-retro-4k.png"); W, Hh = c.size; u = W / 1080
    gradient(c, top=False, h=0.3, k=0.75)
    put(c, shadowed(H("EL RETRO NO SE USA.", 96 * u)), W / 2, Hh - 300 * u)
    put(c, shadowed(H("SE PRESUME.", 150 * u), 0.4), W / 2, Hh - 170 * u)
    put(c, caps("RETRO 3 POR $1,600  ·  FOOTBALLFRENZY.SHOP", 24 * u, SOFT, 0.18), W / 2, Hh - 62 * u)
    put(c, badge(int(130 * u)), W - 100 * u, 100 * u)
    return c


PHOTOS = {"01-viniste-a-ganar": p1_hero, "02-lleva-3-paga-2": p2_trio, "03-no-se-presta": p3_silla,
          "04-tacos-tribuna": p4_tacos, "05-retro-se-presume": p5_retro}


# ------------------------------------------------------------------ videos (overlay + end card)

VW, VH = 1080, 1920
VIDEOS = {
    1: dict(hook=("¿TODAVÍA COMPRAS TUS", "JERSEYS DE UNA EN UNA?"), mid=("AQUÍ TE LLEVAS", "3 POR $1,600"), at=3.6, y=240),
    2: dict(hook=("DEJA DE PAGAR DE MÁS", "POR TU JERSEY."), mid=("3 JERSEYS", "POR $1,600"), at=5.6, y=1480),
}


def overlay(lines, size=100, y=250, sub=False):
    c = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    for i, s in enumerate(lines):
        col = NEON if (sub and i == 1) else WHITE
        put(c, shadowed(H(s, size if i == 0 or not sub else size * 1.35, col), 0.6), VW / 2, y + i * size * 1.12)
    return c


def endcard():
    c = g.background(VW, VH, ((0.5, 0.5, 0.75, (150, 10, 20), 0.36),), base=(6, 6, 7)).copy()
    put(c, badge(300), VW / 2, 520)
    put(c, H("3 JERSEYS", 150), VW / 2, 820)
    put(c, H("POR $1,600", 170, NEON), VW / 2, 990)
    put(c, caps("ENVÍO GRATIS  ·  TALLAS S A 4XL  ·  RASTREO", 26, SOFT, 0.14), VW / 2, 1130)
    put(c, g.cta("COMPRA EN FOOTBALLFRENZY.SHOP", 900, 40), VW / 2, 1300)
    put(c, caps("3X2 AUTOMÁTICO EN EL CARRITO", 26, WHITE, 0.25), VW / 2, 1420)
    return c


def make_video(n):
    src, dst = RAW + f"v{n}.mp4", OUT + f"video-{n}.mp4"
    tmp = g.HERE + "out/hf_ads/tmp/"
    os.makedirs(tmp, exist_ok=True)
    overlay(VIDEOS[n]["hook"]).save(tmp + "hook.png")
    overlay(VIDEOS[n]["mid"], 96, VIDEOS[n]["y"], sub=True).save(tmp + "mid.png")
    endcard().convert("RGB").save(tmp + "end.png")
    at = VIDEOS[n]["at"]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).strip())
    # clip: hook 0-3 s, mid 3.6 s to end; then 3 s end card with crossfade
    fc = (f"[0:v]scale={VW}:{VH}:force_original_aspect_ratio=increase,crop={VW}:{VH},fps=30,setsar=1[b];"
          f"[1:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1,fade=t=out:st=2.7:d=0.3:alpha=1[h];"
          f"[2:v]format=rgba,fade=t=in:st={at}:d=0.3:alpha=1[m];"
          f"[b][h]overlay=0:0:enable='between(t,0,3)'[x];[x][m]overlay=0:0:enable='gte(t,{at})'[v1];"
          f"[3:v]scale={VW}:{VH},fps=30,setsar=1,format=yuv420p[e];"
          f"[v1]format=yuv420p[v1f];[v1f][e]xfade=transition=fade:duration=0.4:offset={dur - 0.4:.2f}[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                    "-loop", "1", "-t", f"{dur:.2f}", "-i", tmp + "hook.png",
                    "-loop", "1", "-t", f"{dur:.2f}", "-i", tmp + "mid.png",
                    "-loop", "1", "-t", "3", "-i", tmp + "end.png",
                    "-filter_complex", fc, "-map", "[out]", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", dst], check=True)
    print(dst)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if "--video" in sys.argv:
        for n in VIDEOS:
            if os.path.exists(RAW + f"v{n}.mp4"):
                make_video(n)
    else:
        for name, fn in PHOTOS.items():
            im = fn().convert("RGB")
            im.save(f"{OUT}{name}.jpg", quality=92, subsampling=0)
            print(name, im.size)
