"""Video street-style (Higgsfield Genjutsu, cambio de persona) + cierre con CTA de marca, sin textos durante el clip.

Entrada: out/hf_ads/raw/cambio.mp4 (resultado de hf_mult_replace_object).
Salida:  out/hf_ads/video-3-barca.mp4 (1080x1920, clip limpio + 3 s de CTA con fundido).
Uso: python3 hf_cambio.py
"""
import os, subprocess
import generar_ads as g
from hf_ads import endcard, VW, VH

RAW = g.HERE + "out/hf_ads/raw/"
OUT = g.HERE + "out/hf_ads/"


def has_audio(path):
    return bool(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", path]).strip())


def main(src=RAW + "cambio.mp4", dst=OUT + "video-3-barca.mp4"):
    tmp = OUT + "tmp/"
    os.makedirs(tmp, exist_ok=True)
    endcard().convert("RGB").save(tmp + "end.png")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).strip())
    off = dur - 0.4
    fc = (f"[0:v]scale={VW}:{VH}:force_original_aspect_ratio=increase:flags=lanczos,crop={VW}:{VH},fps=30,setsar=1,format=yuv420p[a];"
          f"[1:v]scale={VW}:{VH},fps=30,setsar=1,format=yuv420p[e];"
          f"[a][e]xfade=transition=fade:duration=0.4:offset={off:.2f}[v]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-loop", "1", "-t", "3", "-i", tmp + "end.png"]
    maps = ["-map", "[v]"]
    if has_audio(src):
        total = off + 3
        fc += f";[0:a]apad,atrim=0:{total:.2f},afade=t=out:st={total - 1.2:.2f}:d=1.2[au]"
        maps += ["-map", "[au]", "-c:a", "aac", "-b:a", "192k"]
    subprocess.run(cmd + ["-filter_complex", fc] + maps + ["-c:v", "libx264", "-preset", "slow", "-crf", "17",
                          "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst], check=True)
    print(dst)


if __name__ == "__main__":
    main()
