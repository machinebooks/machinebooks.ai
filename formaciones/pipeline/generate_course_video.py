#!/usr/bin/env python3
"""
Pipeline SylvarSec: Speaker Notes → ElevenLabs TTS → ffmpeg → Video curso completo.

Uso:
    python generate_course_video.py --course finops --module 1
    python generate_course_video.py --course finops --all
    python generate_course_video.py --slides-dir ./slides/finops-m01/ --notes ./notes/finops-m01.json

Requisitos:
    pip install elevenlabs python-dotenv Pillow
    ffmpeg instalado y en PATH
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# ─── Configuración ────────────────────────────────────────────────────────────

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    sys.exit("ERROR: ELEVENLABS_API_KEY no configurada. Copia .env.example a .env y añade tu key.")

# Voz y modelo ElevenLabs
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George — cambiar por voz en español preferida
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"

# Directorios
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

# ─── Speaker notes del Módulo 1 FinOps ────────────────────────────────────────

FINOPS_M01_NOTES = [
    {
        "slide": 1,
        "titulo": "Portada",
        "notes": "Bienvenidos al módulo uno: La factura que nadie esperaba. En las próximas cuatro horas, vamos a entender por qué el coste de la inteligencia artificial en producción es el problema que nadie presupuestó, y qué podemos hacer al respecto. Mi nombre es C.P. Sylvar, llevo más de veinte años en ciberseguridad y arquitectura de IA."
    },
    {
        "slide": 2,
        "titulo": "El problema",
        "notes": "Imagina que recibes una factura de cloud el lunes por la mañana. Cuarenta y siete mil dólares. Nadie lo presupuestó. El CFO quiere una explicación para el jueves. Y tú no sabes si el coste viene de los tokens del LLM, de las instancias de GPU, del almacenamiento vectorial, o de todo a la vez. Este es el problema que FinOps para IA viene a resolver."
    },
    {
        "slide": 3,
        "titulo": "Dos ejes del coste",
        "notes": "Este curso tiene un planteamiento único. No hablamos solo de gobernar el coste de la IA, ni solo de optimizar cloud con IA. Hablamos de los dos ejes a la vez, porque en la práctica se cruzan. Un agente inteligente que optimiza tu factura de AWS también genera tokens que cuestan dinero. Si no gobiernas ambos ejes, solo estás moviendo el coste de un lado a otro."
    },
    {
        "slide": 4,
        "titulo": "Anatomía del coste LLM",
        "notes": "Cada llamada a un LLM tiene un coste atómico compuesto de tokens de entrada y tokens de salida. El system prompt se repite en cada llamada y puede representar entre un veinte y un cuarenta por ciento de los tokens de entrada. Los cached tokens, cuando están disponibles, reducen el coste hasta un noventa por ciento en la parte de entrada."
    },
    {
        "slide": 5,
        "titulo": "Pricing atómico por modelo",
        "notes": "Los precios varían hasta veinte veces entre modelos. Un claude-opus-4-6 cuesta quince dólares por millón de tokens de entrada y setenta y cinco de salida. Un haiku cuesta ochenta centavos y cuatro dólares. Elegir el modelo correcto para cada tarea es la primera decisión de optimización. No todas las tareas necesitan el modelo más caro."
    },
    {
        "slide": 6,
        "titulo": "El coste invisible",
        "notes": "Los tokens de entrada y salida son la parte visible de la factura. Pero hay costes invisibles: los embeddings para alimentar tu RAG, el almacenamiento vectorial que crece cada día, los reintentos cuando el modelo devuelve un error. Estos costes invisibles pueden representar entre un quince y un treinta por ciento del total."
    },
    {
        "slide": 7,
        "titulo": "El efecto multiplicador",
        "notes": "Con ciento ocho usuarios y uso moderado, el coste es de trescientos a cuatrocientos dólares al mes. Parece manejable. Pero si llegas a mil usuarios, multiplicas por diez. A diez mil, ya estás en cuarenta mil dólares mensuales solo en tokens. El efecto multiplicador convierte un piloto exitoso en una pesadilla financiera."
    },
    {
        "slide": 8,
        "titulo": "Coste por operación",
        "notes": "No todas las operaciones cuestan lo mismo. Un chat simple cuesta un centavo y medio. Un análisis documental donde el sistema procesa un documento de cincuenta páginas con RAG cuesta ochenta centavos. Y una generación completa con múltiples agentes puede llegar a un dólar treinta y nueve. La diferencia es de cien veces."
    },
    {
        "slide": 9,
        "titulo": "Perfiles de consumo",
        "notes": "Los usuarios no consumen igual. El diez por ciento de power users genera el sesenta por ciento del coste total. Un power user cuesta nueve dólares veintisiete al mes, un light user siete centavos. Identificar estos perfiles es fundamental para implementar showback y que cada equipo entienda su impacto en la factura."
    },
    {
        "slide": 10,
        "titulo": "Anatomía del coste cloud",
        "notes": "El otro eje del coste es la infraestructura cloud. El compute representa entre el cuarenta y cinco y el cincuenta y cinco por ciento. El storage entre quince y veinte. El networking entre diez y quince. Y los servicios gestionados completan el resto. En nuestro caso, la infraestructura anual está entre dieciocho y veinticinco mil dólares."
    },
    {
        "slide": 11,
        "titulo": "Cloud waste global",
        "notes": "Según datos del mercado, entre el veinticinco y el treinta y cinco por ciento del gasto cloud es waste recuperable. Instancias sobredimensionadas, recursos huérfanos que nadie apagó, storage sin políticas de lifecycle. Este es el terreno donde los agentes inteligentes de FinOps generan retorno medible."
    },
    {
        "slide": 12,
        "titulo": "Por qué nadie lo mide",
        "notes": "La razón es organizativa, no técnica. Infraestructura gestiona las máquinas pero no sabe qué modelos se usan. Producto conoce las features pero no su coste unitario. Finanzas ve la factura total pero no puede atribuirla. Y el equipo de IA optimiza la calidad sin mirar el precio. FinOps existe para romper estos silos."
    },
    {
        "slide": 13,
        "titulo": "FinOps como disciplina",
        "notes": "FinOps no es una herramienta, es una disciplina. La FinOps Foundation define un ciclo de tres fases: Inform, donde ganas visibilidad. Optimize, donde reduces waste. Y Operate, donde gobiernas de forma continua. Los seis principios se resumen en una idea: el coste es responsabilidad de todos, no solo de infraestructura."
    },
    {
        "slide": 14,
        "titulo": "FinOps para IA la extensión",
        "notes": "El framework clásico fue diseñado para infra cloud. La IA introduce una unidad nueva: el token. En lugar de rightsizing, haces model routing. En lugar de reserved instances, prompt caching. En lugar de tagging de recursos, atribución por tarea y usuario. Este curso extiende FinOps al mundo de la IA."
    },
    {
        "slide": 15,
        "titulo": "Caso real la Plataforma",
        "notes": "En nuestro caso real, una plataforma con ciento ocho usuarios, el coste de LLM es de trescientos a cuatrocientos dólares al mes. La infra entre mil quinientos y dos mil cien. Pero las personas cuestan entre cinco mil y ocho mil euros. El ROI real está en lo que la IA permite hacer a esas personas, no en el coste del token."
    },
    {
        "slide": 16,
        "titulo": "El coste de no hacer nada",
        "notes": "Si no implementas gobernanza desde el principio, la curva es exponencial. Los usuarios adoptan la IA, los prompts crecen, los agentes encadenan más llamadas. En doce meses sin control puedes pasar de dos mil a veintitrés mil dólares mensuales. Y lo peor no es el coste absoluto, sino no saber de dónde viene."
    },
    {
        "slide": 17,
        "titulo": "Showback vs Chargeback",
        "notes": "Hay dos modelos para responsabilizar a los equipos. Showback les muestra cuánto gastan sin cobrarles. Chargeback les imputa el coste a su presupuesto. Nuestra recomendación: empieza con showback para generar conciencia. Cuando la cultura esté madura, evoluciona a chargeback."
    },
    {
        "slide": 18,
        "titulo": "Los tres pilares",
        "notes": "Todo el curso se estructura alrededor de tres pilares. Visibilidad: sin métricas no hay decisiones. Optimización: reducir waste manteniendo calidad. Y gobernanza: las políticas y alertas que evitan que el coste se descontrole."
    },
    {
        "slide": 19,
        "titulo": "Código calcular coste",
        "notes": "Calcular el coste de una llamada son dos multiplicaciones. Una llamada a Claude Sonnet cuesta menos de dos centavos. Pero con cien mil llamadas al día, esos dos centavos se convierten en cincuenta y ocho mil dólares al mes. Esa es la matemática que hay que tener clara antes de escalar."
    },
    {
        "slide": 20,
        "titulo": "Puntos clave",
        "notes": "Tres ideas para llevarte. Primera: el coste tiene dos ejes que se cruzan. Segunda: el diez por ciento de usuarios genera el sesenta por ciento del coste. Tercera: sin visibilidad, la curva es exponencial. Instrumenta antes de escalar."
    },
    {
        "slide": 21,
        "titulo": "Siguiente módulo",
        "notes": "En el próximo módulo pasaremos de entender el problema a resolverlo. Construiremos LLMUsageLog, conectaremos con las APIs de coste de AWS, Azure y GCP, y sentaremos las bases de la visibilidad total. Nos vemos en el módulo dos."
    },
]


# ─── Funciones del pipeline ───────────────────────────────────────────────────

def generate_audio(notes: list[dict], output_dir: Path) -> list[Path]:
    """Genera MP3 por slide usando ElevenLabs TTS."""
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for item in notes:
        slide_num = item["slide"]
        output_path = output_dir / f"slide_{slide_num:02d}.mp3"

        if output_path.exists():
            print(f"  [SKIP] Slide {slide_num}: {output_path.name} ya existe")
            audio_files.append(output_path)
            continue

        print(f"  [TTS]  Slide {slide_num}: {item['titulo']} ({len(item['notes'])} chars)")

        audio_generator = client.text_to_speech.convert(
            text=item["notes"],
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format=OUTPUT_FORMAT,
        )

        # El SDK devuelve un generador — escribir chunks al fichero
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        audio_files.append(output_path)
        print(f"         → {output_path.name}")

    return audio_files


def get_audio_duration(audio_path: Path) -> float:
    """Obtiene duración en segundos de un MP3 con ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(audio_path),
        ],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def create_slide_video(slide_image: Path, audio_path: Path, output_path: Path):
    """Crea un segmento de vídeo: imagen estática + audio."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(slide_image),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black",
            str(output_path),
        ],
        capture_output=True,
    )


def create_placeholder_slides(num_slides: int, output_dir: Path):
    """Crea slides placeholder (negro con número) si no hay PNGs exportados de Gamma."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit("ERROR: pip install Pillow (necesario para slides placeholder)")

    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(1, num_slides + 1):
        path = output_dir / f"slide_{i:02d}.png"
        if path.exists():
            continue

        # Slide negro con número en verde SylvarSec
        img = Image.new("RGB", (1920, 1080), color=(10, 15, 26))
        draw = ImageDraw.Draw(img)

        # Texto con fuente por defecto
        try:
            font_large = ImageFont.truetype("arial.ttf", 120)
            font_small = ImageFont.truetype("arial.ttf", 36)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Número de slide
        text = f"SLIDE {i}"
        bbox = draw.textbbox((0, 0), text, font=font_large)
        x = (1920 - (bbox[2] - bbox[0])) // 2
        y = (1080 - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), text, fill=(0, 255, 136), font=font_large)

        # Nota: reemplazar con exportaciones reales de Gamma
        note = "Exporta slides desde Gamma como PNG para el video final"
        bbox2 = draw.textbbox((0, 0), note, font=font_small)
        x2 = (1920 - (bbox2[2] - bbox2[0])) // 2
        draw.text((x2, y + 160), note, fill=(192, 200, 208), font=font_small)

        img.save(path)

    print(f"  [IMG]  {num_slides} slides placeholder creados en {output_dir}")


def assemble_video(slides_dir: Path, audio_dir: Path, output_path: Path):
    """Ensambla vídeo final concatenando todos los segmentos slide+audio."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    segments_dir = audio_dir / "segments"
    segments_dir.mkdir(exist_ok=True)

    slide_files = sorted(slides_dir.glob("slide_*.png"))
    audio_files = sorted(audio_dir.glob("slide_*.mp3"))

    if len(slide_files) != len(audio_files):
        print(f"  [WARN] {len(slide_files)} slides vs {len(audio_files)} audios — usando el mínimo")

    num_segments = min(len(slide_files), len(audio_files))
    segment_paths = []

    for i in range(num_segments):
        segment_path = segments_dir / f"segment_{i+1:02d}.mp4"
        print(f"  [VID]  Segmento {i+1}/{num_segments}: {slide_files[i].name} + {audio_files[i].name}")
        create_slide_video(slide_files[i], audio_files[i], segment_path)
        segment_paths.append(segment_path)

    # Crear fichero de concatenación
    concat_file = segments_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg.name}'\n")

    # Concatenar todos los segmentos
    print(f"\n  [MUX]  Ensamblando vídeo final...")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path),
        ],
        capture_output=True,
    )

    # Duración final
    duration = get_audio_duration(output_path)
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    print(f"\n  Video generado: {output_path}")
    print(f"  Duración: {minutes}m {seconds}s")
    print(f"  Tamaño: {output_path.stat().st_size / (1024*1024):.1f} MB")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Pipeline SylvarSec: Notes → Audio → Video")
    parser.add_argument("--course", default="finops", help="ID del curso (finops, ciso, devsecops...)")
    parser.add_argument("--module", type=int, default=1, help="Número de módulo")
    parser.add_argument("--voice", default=VOICE_ID, help="Voice ID de ElevenLabs")
    parser.add_argument("--slides-dir", help="Directorio con PNGs de slides (override)")
    parser.add_argument("--skip-audio", action="store_true", help="Saltar generación de audio")
    parser.add_argument("--skip-video", action="store_true", help="Saltar ensamblaje de vídeo")
    args = parser.parse_args()

    course_id = args.course
    module_num = args.module
    module_dir = OUTPUT_DIR / course_id / f"modulo-{module_num:02d}"

    slides_dir = Path(args.slides_dir) if args.slides_dir else module_dir / "slides"
    audio_dir = module_dir / "audio"
    video_path = module_dir / f"{course_id}-modulo-{module_num:02d}.mp4"

    print(f"\n{'='*60}")
    print(f"  PIPELINE SYLVARSEC")
    print(f"  Curso: {course_id} | Módulo: {module_num}")
    print(f"{'='*60}")

    # Seleccionar notas del módulo
    # Por ahora solo FinOps M01 está hardcodeado — extender con JSON externos
    if course_id == "finops" and module_num == 1:
        notes = FINOPS_M01_NOTES
    else:
        notes_file = BASE_DIR / "notes" / f"{course_id}-m{module_num:02d}.json"
        if notes_file.exists():
            with open(notes_file) as f:
                notes = json.load(f)
        else:
            sys.exit(f"ERROR: No hay notas para {course_id} módulo {module_num}. "
                     f"Crea {notes_file}")

    # Paso 1: Generar slides placeholder si no hay PNGs
    print(f"\n[1/3] SLIDES")
    if not slides_dir.exists() or not list(slides_dir.glob("slide_*.png")):
        print(f"  No hay PNGs en {slides_dir} — creando placeholders")
        print(f"  NOTA: Exporta las slides reales desde Gamma para el vídeo final")
        create_placeholder_slides(len(notes), slides_dir)
    else:
        print(f"  {len(list(slides_dir.glob('slide_*.png')))} slides encontrados en {slides_dir}")

    # Paso 2: Generar audio con ElevenLabs
    if not args.skip_audio:
        print(f"\n[2/3] AUDIO (ElevenLabs)")
        audio_files = generate_audio(notes, audio_dir)
        print(f"  {len(audio_files)} archivos de audio generados")

        # Calcular coste estimado
        total_chars = sum(len(n["notes"]) for n in notes)
        cost_estimate = total_chars * 0.30 / 1000
        print(f"  Caracteres totales: {total_chars:,}")
        print(f"  Coste estimado: ${cost_estimate:.2f}")
    else:
        print(f"\n[2/3] AUDIO — saltado (--skip-audio)")

    # Paso 3: Ensamblar vídeo
    if not args.skip_video:
        print(f"\n[3/3] VIDEO (ffmpeg)")
        assemble_video(slides_dir, audio_dir, video_path)
    else:
        print(f"\n[3/3] VIDEO — saltado (--skip-video)")

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETO")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
