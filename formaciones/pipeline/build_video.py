#!/usr/bin/env python3
"""
Pipeline completo: PPTX > PNG (PowerPoint COM) > MP3 (ElevenLabs) > MP4 (ffmpeg)

Uso:
    python build_video.py "d:/09.GITHUB/formaciones/La-Factura-que-Nadie-Esperaba.pptx"

Requisitos:
    - Windows con PowerPoint instalado
    - pip install elevenlabs python-dotenv python-pptx Pillow
    - ffmpeg en PATH
    - .env con ELEVENLABS_API_KEY
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ─── Config ElevenLabs ────────────────────────────────────────────────────────
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George - cambiar si prefieres otra voz
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"

# ─── Speaker notes Módulo 1 FinOps ───────────────────────────────────────────
SPEAKER_NOTES = [
    "Bienvenidos al módulo uno: La factura que nadie esperaba. En las próximas cuatro horas, vamos a entender por qué el coste de la inteligencia artificial en producción es el problema que nadie presupuestó, y qué podemos hacer al respecto. Mi nombre es C.P. Sylvar, llevo más de veinte años en ciberseguridad y arquitectura de IA.",
    "Imagina que recibes una factura de cloud el lunes por la mañana. Cuarenta y siete mil dólares. Nadie lo presupuestó. El CFO quiere una explicación para el jueves. Y tú no sabes si el coste viene de los tokens del LLM, de las instancias de GPU, del almacenamiento vectorial, o de todo a la vez. Este es el problema que FinOps para IA viene a resolver.",
    "Este curso tiene un planteamiento único. No hablamos solo de gobernar el coste de la IA, ni solo de optimizar cloud con IA. Hablamos de los dos ejes a la vez, porque en la práctica se cruzan. Un agente inteligente que optimiza tu factura de AWS también genera tokens que cuestan dinero. Si no gobiernas ambos ejes, solo estás moviendo el coste de un lado a otro.",
    "Cada llamada a un LLM tiene un coste atómico compuesto de tokens de entrada y tokens de salida. El system prompt se repite en cada llamada y puede representar entre un veinte y un cuarenta por ciento de los tokens de entrada. Los cached tokens, cuando están disponibles, reducen el coste hasta un noventa por ciento en la parte de entrada.",
    "Los precios varían hasta veinte veces entre modelos. Un claude-opus-4-6 cuesta quince dólares por millón de tokens de entrada y setenta y cinco de salida. Un haiku cuesta ochenta centavos y cuatro dólares. Elegir el modelo correcto para cada tarea es la primera decisión de optimización. No todas las tareas necesitan el modelo más caro.",
    "Los tokens de entrada y salida son la parte visible de la factura. Pero hay costes invisibles: los embeddings para alimentar tu RAG, el almacenamiento vectorial que crece cada día, los reintentos cuando el modelo devuelve un error. Estos costes invisibles pueden representar entre un quince y un treinta por ciento del total.",
    "Con ciento ocho usuarios y uso moderado, el coste es de trescientos a cuatrocientos dólares al mes. Parece manejable. Pero si llegas a mil usuarios, multiplicas por diez. A diez mil, ya estás en cuarenta mil dólares mensuales solo en tokens. El efecto multiplicador convierte un piloto exitoso en una pesadilla financiera.",
    "No todas las operaciones cuestan lo mismo. Un chat simple cuesta un centavo y medio. Un análisis documental donde el sistema procesa un documento de cincuenta páginas con RAG cuesta ochenta centavos. Y una generación completa con múltiples agentes puede llegar a un dólar treinta y nueve. La diferencia es de cien veces.",
    "Los usuarios no consumen igual. El diez por ciento de power users genera el sesenta por ciento del coste total. Un power user cuesta nueve dólares veintisiete al mes, un light user siete centavos. Identificar estos perfiles es fundamental para implementar showback y que cada equipo entienda su impacto en la factura.",
    "El otro eje del coste es la infraestructura cloud. El compute representa entre el cuarenta y cinco y el cincuenta y cinco por ciento. El storage entre quince y veinte. El networking entre diez y quince. Y los servicios gestionados completan el resto. En nuestro caso, la infraestructura anual está entre dieciocho y veinticinco mil dólares.",
    "Según datos del mercado, entre el veinticinco y el treinta y cinco por ciento del gasto cloud es waste recuperable. Instancias sobredimensionadas, recursos huérfanos que nadie apagó, storage sin políticas de lifecycle. Este es el terreno donde los agentes inteligentes de FinOps generan retorno medible.",
    "La razón es organizativa, no técnica. Infraestructura gestiona las máquinas pero no sabe qué modelos se usan. Producto conoce las features pero no su coste unitario. Finanzas ve la factura total pero no puede atribuirla. Y el equipo de IA optimiza la calidad sin mirar el precio. FinOps existe para romper estos silos.",
    "FinOps no es una herramienta, es una disciplina. La FinOps Foundation define un ciclo de tres fases: Inform, donde ganas visibilidad. Optimize, donde reduces waste. Y Operate, donde gobiernas de forma continua. Los seis principios se resumen en una idea: el coste es responsabilidad de todos, no solo de infraestructura.",
    "El framework clásico fue diseñado para infra cloud. La IA introduce una unidad nueva: el token. En lugar de rightsizing, haces model routing. En lugar de reserved instances, prompt caching. En lugar de tagging de recursos, atribución por tarea y usuario. Este curso extiende FinOps al mundo de la IA.",
    "En nuestro caso real, una plataforma con ciento ocho usuarios, el coste de LLM es de trescientos a cuatrocientos dólares al mes. La infra entre mil quinientos y dos mil cien. Pero las personas cuestan entre cinco mil y ocho mil euros. El ROI real está en lo que la IA permite hacer a esas personas, no en el coste del token.",
    "Si no implementas gobernanza desde el principio, la curva es exponencial. Los usuarios adoptan la IA, los prompts crecen, los agentes encadenan más llamadas. En doce meses sin control puedes pasar de dos mil a veintitrés mil dólares mensuales. Y lo peor no es el coste absoluto, sino no saber de dónde viene.",
    "Hay dos modelos para responsabilizar a los equipos. Showback les muestra cuánto gastan sin cobrarles. Chargeback les imputa el coste a su presupuesto. Nuestra recomendación: empieza con showback para generar conciencia. Cuando la cultura esté madura, evoluciona a chargeback.",
    "Todo el curso se estructura alrededor de tres pilares. Visibilidad: sin métricas no hay decisiones. Optimización: reducir waste manteniendo calidad. Y gobernanza: las políticas y alertas que evitan que el coste se descontrole.",
    "Calcular el coste de una llamada son dos multiplicaciones. Una llamada a Claude Sonnet cuesta menos de dos centavos. Pero con cien mil llamadas al día, esos dos centavos se convierten en cincuenta y ocho mil dólares al mes. Esa es la matemática que hay que tener clara antes de escalar.",
    "Tres ideas para llevarte. Primera: el coste tiene dos ejes que se cruzan. Segunda: el diez por ciento de usuarios genera el sesenta por ciento del coste. Tercera: sin visibilidad, la curva es exponencial. Instrumenta antes de escalar.",
    "En el próximo módulo pasaremos de entender el problema a resolverlo. Construiremos LLMUsageLog, conectaremos con las APIs de coste de AWS, Azure y GCP, y sentaremos las bases de la visibilidad total. Nos vemos en el módulo dos.",
]


# ─── Paso 1: Exportar PPTX a PNG con PowerPoint COM ──────────────────────────

def export_pptx_to_png(pptx_path: Path, output_dir: Path) -> list[Path]:
    """Usa PowerPoint COM automation para exportar cada slide como PNG 1920x1080."""
    import comtypes.client

    output_dir.mkdir(parents=True, exist_ok=True)
    pptx_abs = str(pptx_path.resolve())

    print(f"  Abriendo PowerPoint...")
    powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
    powerpoint.Visible = 1

    presentation = powerpoint.Presentations.Open(pptx_abs, WithWindow=False)
    num_slides = presentation.Slides.Count
    print(f"  {num_slides} slides detectados")

    png_files = []
    for i in range(1, num_slides + 1):
        slide = presentation.Slides(i)
        png_path = output_dir / f"slide_{i:02d}.png"
        slide.Export(str(png_path.resolve()), "PNG", 1920, 1080)
        png_files.append(png_path)
        print(f"  [PNG]  Slide {i}/{num_slides} > {png_path.name}")

    presentation.Close()
    powerpoint.Quit()
    print(f"  {num_slides} slides exportados")
    return png_files


# ─── Paso 2: Generar audio con ElevenLabs ────────────────────────────────────

def generate_audio(notes: list[str], output_dir: Path) -> list[Path]:
    """Genera MP3 por slide usando ElevenLabs TTS."""
    from elevenlabs.client import ElevenLabs

    if not ELEVENLABS_API_KEY:
        sys.exit("ERROR: ELEVENLABS_API_KEY no configurada en .env")

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, text in enumerate(notes, 1):
        output_path = output_dir / f"slide_{i:02d}.mp3"

        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"  [SKIP] Slide {i}: ya existe ({output_path.stat().st_size // 1024} KB)")
            audio_files.append(output_path)
            continue

        print(f"  [TTS]  Slide {i}/{len(notes)} ({len(text)} chars)...", end=" ", flush=True)

        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format=OUTPUT_FORMAT,
        )

        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        size_kb = output_path.stat().st_size // 1024
        print(f"OK ({size_kb} KB)")
        audio_files.append(output_path)

        # Rate limit: pequeña pausa entre llamadas
        time.sleep(0.5)

    return audio_files


# ─── Paso 3: Ensamblar vídeo con ffmpeg ──────────────────────────────────────

def get_duration(file_path: Path) -> float:
    """Duración en segundos via ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(file_path),
        ],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def build_video(slides_dir: Path, audio_dir: Path, output_path: Path):
    """Ensambla MP4 final: cada slide PNG + su audio MP3."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    segments_dir = output_path.parent / "segments"
    segments_dir.mkdir(exist_ok=True)

    slide_files = sorted(slides_dir.glob("slide_*.png"))
    audio_files = sorted(audio_dir.glob("slide_*.mp3"))

    n = min(len(slide_files), len(audio_files))
    if n == 0:
        sys.exit("ERROR: No hay slides o audios para ensamblar")

    if len(slide_files) != len(audio_files):
        print(f"  [WARN] {len(slide_files)} PNGs vs {len(audio_files)} MP3s - usando {n}")

    segment_paths = []
    total_duration = 0

    for i in range(n):
        seg_path = segments_dir / f"seg_{i+1:02d}.mp4"
        print(f"  [SEG]  {i+1}/{n}: {slide_files[i].name} + {audio_files[i].name}...", end=" ", flush=True)

        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(slide_files[i]),
                "-i", str(audio_files[i]),
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black",
                str(seg_path),
            ],
            capture_output=True, text=True,
        )

        if result.returncode != 0:
            print(f"FAIL")
            print(f"    stderr: {result.stderr[-200:]}")
            continue

        dur = get_duration(seg_path)
        total_duration += dur
        print(f"OK ({dur:.1f}s)")
        segment_paths.append(seg_path)

    # Concatenar
    concat_file = segments_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segment_paths:
            # Usar ruta absoluta con barras normales para ffmpeg en Windows
            f.write(f"file '{seg.resolve().as_posix()}'\n")

    print(f"\n  [MUX]  Concatenando {len(segment_paths)} segmentos...")
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path),
        ],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print(f"  ERROR concat: {result.stderr[-300:]}")
        sys.exit(1)

    minutes = int(total_duration // 60)
    seconds = int(total_duration % 60)
    size_mb = output_path.stat().st_size / (1024 * 1024)

    print(f"\n  {'='*50}")
    print(f"  VIDEO GENERADO: {output_path}")
    print(f"  Slides: {len(segment_paths)}")
    print(f"  Duración: {minutes}m {seconds}s")
    print(f"  Tamaño: {size_mb:.1f} MB")
    print(f"  {'='*50}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline SylvarSec: PPTX > PNG > MP3 > MP4"
    )
    parser.add_argument(
        "pptx",
        help="Ruta al fichero PPTX de Gamma",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Directorio de salida (default: junto al PPTX)",
    )
    parser.add_argument(
        "--voice", "-v",
        default=VOICE_ID,
        help=f"ElevenLabs Voice ID (default: {VOICE_ID})",
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Saltar exportación PPTX>PNG (usar PNGs existentes)",
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Saltar generación de audio (usar MP3s existentes)",
    )
    parser.add_argument(
        "--skip-video",
        action="store_true",
        help="Saltar ensamblaje de vídeo",
    )
    args = parser.parse_args()

    voice_id = args.voice

    pptx_path = Path(args.pptx).resolve()
    if not pptx_path.exists():
        sys.exit(f"ERROR: No existe {pptx_path}")

    # Directorio de salida
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = pptx_path.parent / pptx_path.stem

    slides_dir = out_dir / "slides"
    audio_dir = out_dir / "audio"
    video_path = out_dir / f"{pptx_path.stem}.mp4"

    print(f"\n{'='*60}")
    print(f"  PIPELINE SYLVARSEC - PPTX > VIDEO")
    print(f"  Input:  {pptx_path}")
    print(f"  Output: {out_dir}")
    print(f"{'='*60}")

    # Paso 1: PPTX > PNG
    print(f"\n[1/3] EXPORTAR SLIDES")
    if args.skip_export:
        existing = list(slides_dir.glob("slide_*.png"))
        print(f"  Saltado - {len(existing)} PNGs existentes")
    else:
        try:
            export_pptx_to_png(pptx_path, slides_dir)
        except ImportError:
            print("  ERROR: pip install comtypes (necesario para PowerPoint COM)")
            print("  Alternativa: exporta manualmente desde PowerPoint como PNG")
            sys.exit(1)
        except Exception as e:
            print(f"  ERROR PowerPoint COM: {e}")
            print("  Alternativa: abre el PPTX en PowerPoint > Archivo > Exportar > PNG")
            sys.exit(1)

    # Verificar slides
    slide_count = len(list(slides_dir.glob("slide_*.png")))
    notes_count = len(SPEAKER_NOTES)
    if slide_count == 0:
        sys.exit(f"ERROR: No hay PNGs en {slides_dir}")

    if slide_count != notes_count:
        print(f"\n  [INFO] {slide_count} slides vs {notes_count} notas de narración")
        print(f"  Se procesarán {min(slide_count, notes_count)} slides con audio")

    # Paso 2: Generar audio
    print(f"\n[2/3] GENERAR AUDIO (ElevenLabs)")
    if args.skip_audio:
        existing = list(audio_dir.glob("slide_*.mp3"))
        print(f"  Saltado - {len(existing)} MP3s existentes")
    else:
        # Solo generar audio para las slides que existen
        notes_to_generate = SPEAKER_NOTES[:slide_count]
        total_chars = sum(len(n) for n in notes_to_generate)
        cost = total_chars * 0.30 / 1000
        print(f"  {len(notes_to_generate)} slides, {total_chars:,} caracteres")
        print(f"  Coste estimado: ${cost:.2f}")
        print()
        generate_audio(notes_to_generate, audio_dir)

    # Paso 3: Ensamblar vídeo
    print(f"\n[3/3] ENSAMBLAR VIDEO (ffmpeg)")
    if args.skip_video:
        print(f"  Saltado")
    else:
        build_video(slides_dir, audio_dir, video_path)

    print(f"\n  PIPELINE COMPLETO\n")


if __name__ == "__main__":
    main()
