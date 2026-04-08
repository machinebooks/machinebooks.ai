#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera slides SylvarSec con Pillow y ensambla video con audio existente."""

import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("pip install Pillow")

OUTPUT_DIR = Path("d:/09.GITHUB/formaciones/piloto-consultor")
AUDIO_DIR = OUTPUT_DIR / "audio"
SLIDES_DIR = OUTPUT_DIR / "slides"
SEGMENTS_DIR = OUTPUT_DIR / "segments"
VIDEO_PATH = OUTPUT_DIR / "piloto-consultor-m01.mp4"

# Colores SylvarSec
BG = (10, 15, 26)        # #0A0F1A
GREEN = (0, 255, 136)    # #00FF88
WHITE = (255, 255, 255)
GRAY = (192, 200, 208)   # #C0C8D0
DARK_GRAY = (60, 70, 85)

SLIDES_CONTENT = [
    {
        "terminal": "~/sylvarsec $ ./training --course consultor --module 1",
        "title": "La Crisis Silenciosa\nde la Consultoría",
        "subtitle": "El Consultor y la Máquina — Módulo 1 de 10",
        "footer": "C.P. Sylvar | sylvarsec.com",
    },
    {
        "terminal": "~/sylvarsec $ cat factura.log",
        "title": "€14.000",
        "subtitle": "120 horas de trabajo\npara acabar segundos por precio",
        "footer": "3 consultores · 14 días · 287 páginas de pliego",
    },
    {
        "terminal": "~/sylvarsec $ analyze --sector consultoria",
        "title": "La Crisis en Números",
        "subtitle": "Márgenes: 35% → 15%\nÉxito en propuestas: 15-30%\n"
                    "Coste por propuesta: +80 horas\nRotación seniors: 18-22%\n"
                    "Automatizable con IA: 40-60%",
        "footer": "Fuente: Flexera, McKinsey, datos del sector",
    },
    {
        "terminal": "~/sylvarsec $ diff junior.time llm.time",
        "title": "La Commoditización",
        "subtitle": "Lo que un junior tardaba 3 días\nun LLM lo responde en 4 minutos\n\n"
                    "El cliente pregunta:\n¿Por qué pago €150/hora por esto?",
        "footer": "No es un problema de talento. Es un problema de modelo.",
    },
    {
        "terminal": "~/sylvarsec $ cat resultados.json",
        "title": "El Impacto Real",
        "subtitle": "Propuestas: 120h → 20h  (-83%)\n"
                    "Informes: 3 días → 4 horas\n"
                    "Análisis RFP: 2 días → 15 min\n"
                    "Coste análisis: $0.80 vs €600\n"
                    "Knowledge base: 12 años indexados",
        "footer": "Datos medidos, no promesas.",
    },
]


def create_slide(content: dict, output_path: Path):
    img = Image.new("RGB", (1920, 1080), color=BG)
    draw = ImageDraw.Draw(img)

    # Intentar cargar JetBrains Mono, fallback a Consolas/Arial
    try:
        font_terminal = ImageFont.truetype("consola.ttf", 28)
        font_title = ImageFont.truetype("consolab.ttf", 72)
        font_subtitle = ImageFont.truetype("consola.ttf", 36)
        font_footer = ImageFont.truetype("consola.ttf", 24)
    except OSError:
        try:
            font_terminal = ImageFont.truetype("arial.ttf", 28)
            font_title = ImageFont.truetype("arialbd.ttf", 72)
            font_subtitle = ImageFont.truetype("arial.ttf", 36)
            font_footer = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font_terminal = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
            font_footer = ImageFont.load_default()

    # Línea superior decorativa
    draw.rectangle([0, 0, 1920, 4], fill=GREEN)

    # Terminal prompt
    draw.text((80, 40), content["terminal"], fill=GREEN, font=font_terminal)

    # Línea separadora
    draw.line([(80, 85), (1840, 85)], fill=DARK_GRAY, width=1)

    # Título
    title_lines = content["title"].split("\n")
    y = 180
    for line in title_lines:
        # Si es un número grande (dato), hacerlo más grande y en verde
        if line.strip().startswith("€") or line.strip().startswith("$"):
            try:
                font_big = ImageFont.truetype("consolab.ttf", 120)
            except OSError:
                font_big = font_title
            draw.text((80, y), line, fill=GREEN, font=font_big)
            y += 140
        else:
            draw.text((80, y), line, fill=WHITE, font=font_title)
            y += 85

    # Subtítulo
    y += 30
    for line in content["subtitle"].split("\n"):
        if line.strip():
            # Detectar flechas y porcentajes para colorear
            if "→" in line or "%" in line or "$" in line or "€" in line:
                draw.text((80, y), line, fill=GREEN, font=font_subtitle)
            else:
                draw.text((80, y), line, fill=GRAY, font=font_subtitle)
        y += 48

    # Footer
    draw.line([(80, 1000), (1840, 1000)], fill=DARK_GRAY, width=1)
    draw.text((80, 1020), content["footer"], fill=DARK_GRAY, font=font_footer)

    # Marca SylvarSec
    draw.text((1500, 1020), "SylvarSec", fill=GREEN, font=font_footer)

    # Línea inferior decorativa
    draw.rectangle([0, 1076, 1920, 1080], fill=GREEN)

    img.save(output_path)


def get_duration(file_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(file_path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def main():
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  VIDEO CONSULTOR - Slides + Audio + Ensamblaje")
    print(f"{'='*60}")

    # 1. Crear slides
    print(f"\n[1/3] CREAR SLIDES SYLVARSEC")
    for i, content in enumerate(SLIDES_CONTENT, 1):
        slide_path = SLIDES_DIR / f"slide_{i:02d}.png"
        create_slide(content, slide_path)
        print(f"  [PNG] Slide {i}/5: {content['title'].split(chr(10))[0]}")

    # 2. Ensamblar segmentos
    print(f"\n[2/3] ENSAMBLAR SEGMENTOS")
    slide_files = sorted(SLIDES_DIR.glob("slide_*.png"))
    audio_files = sorted(AUDIO_DIR.glob("slide_*.mp3"))
    n = min(len(slide_files), len(audio_files))

    segment_paths = []
    total_dur = 0

    for i in range(n):
        seg_path = SEGMENTS_DIR / f"seg_{i+1:02d}.mp4"
        print(f"  [SEG]  {i+1}/{n}...", end=" ", flush=True)

        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(slide_files[i]),
                "-i", str(audio_files[i]),
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-pix_fmt", "yuv420p",
                "-vf", "scale=1920:1080",
                str(seg_path),
            ],
            capture_output=True, text=True,
        )

        if result.returncode != 0:
            print(f"FAIL: {result.stderr[-200:]}")
            continue

        dur = get_duration(seg_path)
        total_dur += dur
        print(f"OK ({dur:.0f}s / {dur/60:.1f}min)")
        segment_paths.append(seg_path)

    # 3. Concatenar
    print(f"\n[3/3] CONCATENAR VIDEO FINAL")
    concat_file = SEGMENTS_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg.resolve().as_posix()}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_file), "-c", "copy", str(VIDEO_PATH)],
        capture_output=True,
    )

    minutes = int(total_dur // 60)
    seconds = int(total_dur % 60)
    size_mb = VIDEO_PATH.stat().st_size / (1024 * 1024)

    print(f"\n  {'='*50}")
    print(f"  VIDEO CONSULTOR GENERADO")
    print(f"  Archivo: {VIDEO_PATH}")
    print(f"  Slides: {len(segment_paths)}")
    print(f"  Duracion: {minutes}m {seconds}s")
    print(f"  Tamano: {size_mb:.1f} MB")
    print(f"  Media: {total_dur/len(segment_paths):.0f}s ({total_dur/len(segment_paths)/60:.1f} min/slide)")
    print(f"  {'='*50}\n")


if __name__ == "__main__":
    main()
