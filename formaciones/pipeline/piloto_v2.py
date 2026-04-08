#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Piloto v2: texto corregido con tildes, puntuación y pronunciación guiada."""

import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    sys.exit("ERROR: ELEVENLABS_API_KEY no configurada")

from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"

SLIDES_DIR = Path("d:/09.GITHUB/formaciones/La-Factura-que-Nadie-Esperaba/slides")
OUTPUT_DIR = Path("d:/09.GITHUB/formaciones/piloto-v2")

# ============================================================================
# NARRACIÓN CORREGIDA — Español con tildes, puntuación completa,
# siglas espaciadas, términos técnicos pronunciables
# ============================================================================

NOTES = [
    # SLIDE 1 — PORTADA
    (
        "Bienvenidos al módulo uno: La factura que nadie esperaba. "
        "En las próximas cuatro horas, vamos a entender por qué el coste "
        "de la inteligencia artificial en producción es el problema que nadie "
        "presupuestó, y qué podemos hacer al respecto. Mi nombre es "
        "C. P. Sylvar, llevo más de veinte años en ciberseguridad y "
        "arquitectura de inteligencia artificial.\n\n"

        "No hablo de un coste teórico. Hablo de facturas reales. De ese "
        "correo que llega un martes a las nueve de la mañana con asunto "
        "escueto: factura API Anthropic, marzo. Y la cifra triplica la "
        "previsión trimestral. En menos de una hora, tres preguntas aterrizan "
        "en el canal de Slack del equipo de ingeniería. Primera: qué equipo "
        "o servicio consumió cada bloque de tokens. Segunda: por qué este "
        "mes cuesta el doble que el anterior, si no hemos lanzado "
        "funcionalidad nueva. Tercera: estamos pagando por modelos o "
        "pipelines que ya no usa nadie.\n\n"

        "Nadie tiene respuesta para ninguna de las tres. Y ese es el punto "
        "de partida de este curso.\n\n"

        "Este módulo lo estructuramos en tres bloques. Primero, vamos a "
        "entender la anatomía del problema: por qué el coste de la "
        "inteligencia artificial es tan difícil de gobernar y por qué las "
        "herramientas tradicionales de FinOps no cubren este escenario. "
        "Segundo, vamos a analizar los datos reales de un caso de estudio, "
        "con facturas medidas, perfiles de consumo reales y las decisiones "
        "que tomamos para gobernarlos. Y tercero, vamos a escribir nuestras "
        "primeras líneas de código para calcular, registrar y visualizar "
        "costes de llamadas a modelos de lenguaje.\n\n"

        "Si trabajan como FinOps Engineers, Cloud Architects, Engineering "
        "Managers o directores de tecnología, este módulo les dará el marco "
        "conceptual y las herramientas prácticas para entender de dónde "
        "viene cada euro de su factura de inteligencia artificial. Y lo que "
        "es más importante: les dará la capacidad de actuar sobre ese coste "
        "antes de que se descontrole.\n\n"

        "Empecemos."
    ),

    # SLIDE 2 — EL PROBLEMA ($47.000)
    (
        "Cuarenta y siete mil dólares. Esa es la cifra que aparece en la "
        "pantalla. Una factura de cloud que nadie presupuestó. El director "
        "financiero quiere una explicación para el jueves. Y tú, como "
        "responsable técnico, no sabes si el coste viene de los tokens del "
        "modelo de lenguaje, de las instancias de GPU, del almacenamiento "
        "vectorial, o de todo a la vez.\n\n"

        "Este escenario no es hipotético. Es exactamente lo que ocurre "
        "cuando una organización despliega inteligencia artificial sin "
        "gobernanza de costes. Y la progresión siempre sigue el mismo "
        "patrón.\n\n"

        "El primer mes, la factura es baja. El equipo está en fase de "
        "prototipo, con pocos usuarios y prompts cortos. La cifra se diluye "
        "en la partida general de cloud. Nadie la mira. El segundo mes, el "
        "producto pasa a producción. Cincuenta usuarios empiezan a generar "
        "consultas reales. El consumo de tokens se multiplica por ocho, pero "
        "la factura tarda treinta días en llegar. Cuando la ves, ya es "
        "historia. El tercer mes, alguien activa un agente autónomo que "
        "encadena llamadas para análisis documental. El consumo se dispara "
        "un trescientos por ciento en una semana. El cuarto mes llega la "
        "factura consolidada del trimestre. El director financiero convoca "
        "una reunión de urgencia.\n\n"

        "Un estudio de Andreessen Horowitz sobre startups con inteligencia "
        "artificial en producción estimó que el coste de inferencia "
        "representa entre el veinte y el cuarenta por ciento del coste de "
        "los bienes vendidos de compañías con productos basados en modelos "
        "generativos. Para una startup que factura cien mil euros al mes, "
        "eso implica entre veinte mil y cuarenta mil euros solo en llamadas "
        "a modelos. Sin contar infraestructura.\n\n"

        "En entornos enterprise, el patrón es distinto pero igual de "
        "dañino. Cada departamento adopta inteligencia artificial a su "
        "ritmo. Marketing contrata una herramienta de generación de "
        "contenido. Legal activa un servicio de análisis de contratos. "
        "Ingeniería despliega agentes de asistencia al desarrollo. Cada uno "
        "negocia su propia clave de API con su propio proveedor. El "
        "resultado: seis facturas de inteligencia artificial distintas que "
        "nadie consolida, seis patrones de consumo que nadie compara, y un "
        "gasto total que supera el presupuesto de infraestructura cloud sin "
        "que ningún equipo individual lo perciba.\n\n"

        "El coste de no gobernar no es solo financiero. Es un coste de "
        "oportunidad. Sin datos de consumo, la organización no puede "
        "responder preguntas estratégicas. ¿Qué funcionalidad aporta más "
        "valor por euro invertido? ¿Deberíamos invertir más en el agente de "
        "análisis de riesgos o en el chatbot de soporte? ¿Cuánto nos "
        "costaría escalar el servicio a quinientos usuarios? Sin gobernanza, "
        "cada decisión de inversión es una apuesta. Y las apuestas, en "
        "entornos corporativos, suelen acabar con alguien pidiendo que se "
        "apague todo."
    ),

    # SLIDE 3 — DOS EJES DEL COSTE
    (
        "Este curso tiene un planteamiento que lo diferencia de cualquier "
        "otro material sobre FinOps. No hablamos solo de gobernar el coste "
        "de la inteligencia artificial. No hablamos solo de optimizar cloud "
        "con inteligencia artificial. Hablamos de los dos ejes a la vez, "
        "porque en la práctica se cruzan de formas que la mayoría de los "
        "frameworks no contemplan.\n\n"

        "El eje A es FinOps para inteligencia artificial. Gobernar el coste "
        "de tokens, modelos, pipelines de generación aumentada por "
        "recuperación, agentes autónomos y herramientas de protocolo de "
        "contexto de modelo. Saber cuánto cuesta cada funcionalidad en "
        "producción. Asignar ese coste a equipos, productos o clientes. "
        "Detectar anomalías. Establecer políticas de selección de modelo "
        "según la tarea. Implementar circuit breakers de coste que impidan "
        "que un agente desbocado genere una factura de cinco cifras en una "
        "noche.\n\n"

        "El eje B es Cloud FinOps con inteligencia artificial. Construir "
        "agentes inteligentes que analicen el gasto cloud, detecten waste, "
        "recomienden optimizaciones y, en algunos casos, las ejecuten de "
        "forma autónoma. Usar Claude Agent SDK y Claude Code para crear "
        "herramientas que lean Cost Explorer, identifiquen recursos "
        "infrautilizados, propongan rightsizing y generen informes "
        "ejecutivos.\n\n"

        "Lo interesante ocurre donde los dos ejes se cruzan. El agente de "
        "optimización cloud del eje B consume tokens que necesitan la "
        "gobernanza del eje A. La infraestructura que soporta los modelos "
        "del eje A necesita la optimización del eje B. No son dos "
        "disciplinas separadas. Son dos caras del mismo problema.\n\n"

        "Pongamos un ejemplo concreto. Imagina que construyes un agente con "
        "Claude Agent SDK que cada mañana consulta el Cost Explorer de AWS, "
        "identifica instancias sobredimensionadas y envía un informe al "
        "equipo de infraestructura. Ese agente te ahorra quinientos dólares "
        "al mes en instancias. Fantástico. Pero el agente en sí consume "
        "tokens: cada llamada a Claude para analizar los datos, cada "
        "invocación de tool use para consultar las APIs de AWS, cada "
        "generación del informe final. Si no mides el coste del agente, no "
        "sabes si tu herramienta de ahorro es rentable.\n\n"

        "En nuestro caso real, un agente de análisis de costes cloud "
        "consume entre dos y cuatro dólares al mes en tokens. Ahorra entre "
        "trescientos y quinientos dólares. El retorno de inversión es claro. "
        "Pero sin medición, ese dato no existe. Y sin ese dato, el director "
        "financiero tiene todo el derecho a preguntar: estamos gastando "
        "dinero en inteligencia artificial para ahorrar dinero en cloud, "
        "¿y cuánto nos cuesta exactamente ese ahorro?\n\n"

        "A lo largo de los diez módulos de este curso, construiremos ambos "
        "ejes. Con código real. Con decisiones documentadas y sus "
        "alternativas descartadas. Con las facturas reales que motivaron "
        "cada decisión. Y con la honestidad de explicar qué funcionó, qué "
        "no, y qué todavía no sabemos resolver."
    ),

    # SLIDE 4 — ANATOMÍA DEL COSTE
    (
        "Vamos a entrar en la parte técnica. Para gobernar el coste de un "
        "modelo de lenguaje, primero hay que entender su anatomía. Y el "
        "primer concepto que cambia la forma de ver una factura es la "
        "asimetría de precios entre tokens de entrada y tokens de salida.\n\n"

        "Los modelos no cobran lo mismo por leer que por generar. Para "
        "Claude Sonnet cuatro punto seis, el precio es de tres dólares por "
        "millón de tokens de entrada y quince dólares por millón de tokens "
        "de salida. La ratio es uno a cinco. Esto significa que un sistema "
        "que genera respuestas largas paga cinco veces más por token de "
        "salida que por token de entrada.\n\n"

        "Veamos el contraste con números concretos. Una tarea de "
        "clasificación de documentos usa ochocientos tokens de entrada y "
        "genera cinco tokens de salida: una etiqueta. Con Claude Haiku "
        "cuatro punto cinco, el coste por clasificación es de menos de una "
        "centésima de centavo. Prácticamente gratis. Una tarea de generación "
        "de informe usa tres mil tokens de entrada y genera cuatro mil de "
        "salida. Con el mismo modelo, el coste es casi dos centavos. "
        "Doscientas setenta y nueve veces más cara. Si el equipo trata "
        "ambas tareas como llamadas a un modelo de lenguaje sin distinguir "
        "el perfil de entrada y salida, las decisiones de presupuesto serán "
        "erróneas. Diez mil clasificaciones al mes cuestan sesenta y seis "
        "centavos. Diez mil informes cuestan ciento ochenta y cuatro "
        "dólares.\n\n"

        "Hay un tercer tipo de token que modifica este cálculo: los tokens "
        "cacheados. Cuando una llamada reutiliza un prefijo de contexto que "
        "ya fue procesado, el proveedor cobra ese prefijo a precio reducido. "
        "Anthropic aplica un descuento del noventa por ciento sobre los "
        "tokens de entrada cacheados: treinta centavos por millón en lugar "
        "de tres dólares. Para sistemas con prompts de sistema extensos que "
        "se repiten en cada llamada, la diferencia entre activar o no la "
        "caché puede representar entre el cuarenta y el setenta por ciento "
        "del coste mensual de entrada.\n\n"

        "Les cuento un caso real. En la Plataforma, el servicio de análisis "
        "normativo regeneraba el bloque de instrucciones en cada llamada "
        "porque el prompt de sistema variaba ligeramente según el idioma del "
        "documento. Una variación de dos caracteres en el prefijo anulaba la "
        "caché. Tres días de análisis a pleno rendimiento con caché "
        "desactivada. Trescientos doce euros en un pico que nadie entendió "
        "hasta que alguien revisó los logs token por token.\n\n"

        "El contraejemplo es igual de instructivo. Otro equipo descubrió "
        "que su caché de prompts funcionaba demasiado bien. El prompt de "
        "sistema cacheado tenía instrucciones desactualizadas. Durante dos "
        "semanas, el modelo respondió con un comportamiento obsoleto a un "
        "coste reducido. Ahorrar en tokens no sirve de nada si las "
        "respuestas son incorrectas. La caché exige disciplina de "
        "invalidación: saber cuándo borrarla es tan importante como saber "
        "cuándo activarla.\n\n"

        "Estos son los detalles que marcan la diferencia entre un equipo "
        "que dice: gastamos tanto en inteligencia artificial; y un equipo "
        "que dice: gastamos tanto en inteligencia artificial, sabemos "
        "exactamente por qué, y podemos optimizarlo."
    ),

    # SLIDE 5 — PRICING POR MODELO
    (
        "Ahora que entendemos la estructura de tokens, veamos los números "
        "concretos. En la pantalla tienen la tabla de precios por modelo. "
        "Quiero que se fijen en la diferencia de coste entre modelos, "
        "porque esta tabla es la base de una de las decisiones de "
        "optimización más potentes que veremos en este curso: el routing "
        "inteligente de modelos.\n\n"

        "Claude Opus cuatro punto seis, el modelo más capaz de Anthropic, "
        "cuesta quince dólares por millón de tokens de entrada y setenta y "
        "cinco dólares por millón de salida. Es el modelo que usas cuando "
        "necesitas razonamiento complejo, análisis multi-paso, o generación "
        "de alta calidad. Pero no todas las tareas lo necesitan.\n\n"

        "Claude Sonnet cuatro punto seis cuesta tres dólares por millón de "
        "entrada y quince de salida. Es cinco veces más barato que Opus. "
        "Para la mayoría de tareas de producción: el análisis de documentos, "
        "la generación de informes estándar, la respuesta a preguntas con "
        "contexto, Sonnet ofrece una calidad muy cercana a Opus a una "
        "quinta parte del precio.\n\n"

        "Claude Haiku cuatro punto cinco cuesta ochenta centavos de entrada "
        "y cuatro dólares de salida. Es casi veinte veces más barato que "
        "Opus. Para tareas simples como clasificación, extracción de "
        "entidades, validación de formato o respuestas cortas, Haiku es más "
        "que suficiente.\n\n"

        "La pregunta que debe hacerse todo equipo es: qué porcentaje de "
        "nuestras llamadas realmente necesita el modelo más caro. En "
        "nuestro caso, cuando analizamos el patrón de uso de la Plataforma, "
        "descubrimos que el sesenta y ocho por ciento de las llamadas eran "
        "tareas que Haiku podía resolver con la misma calidad que Sonnet. "
        "Un doce por ciento eran tareas que requerían Sonnet. Y solo un "
        "veinte por ciento necesitaba la capacidad de Opus.\n\n"

        "Antes de implementar routing de modelos, todas las llamadas iban a "
        "Sonnet. El coste mensual era de cuatrocientos treinta y nueve "
        "dólares. Después de implementar un router que selecciona el modelo "
        "según la complejidad de la tarea, el coste bajó a ciento ochenta y "
        "dos dólares. Una reducción del sesenta por ciento. Sin degradar la "
        "calidad percibida por el usuario.\n\n"

        "Pero ojo, el routing no es gratis en términos de complejidad. "
        "Necesitas un clasificador de tareas. Necesitas definir criterios de "
        "cuándo usar cada modelo. Necesitas monitorizar la calidad de las "
        "respuestas para asegurarte de que Haiku no está fallando en tareas "
        "que deberían ir a Sonnet. Y necesitas medir el coste del propio "
        "router, que a su vez consume tokens.\n\n"

        "Estos son los trade-offs reales de los que hablaremos en "
        "profundidad en el módulo tres. Por ahora, lo importante es que "
        "interioricen esta tabla de precios. Porque cada decisión de diseño, "
        "cada prompt, cada agente que construyan, tiene un coste atómico que "
        "se deriva directamente de estos números. Y gobernar ese coste "
        "empieza por conocerlo.\n\n"

        "En el siguiente bloque vamos a ver cómo se suman estos costes "
        "atómicos para formar la factura total, incluyendo los costes "
        "invisibles que la mayoría de los equipos ni siquiera saben que "
        "están pagando."
    ),
]


def get_duration(file_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(file_path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def main():
    audio_dir = OUTPUT_DIR / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    total_chars = sum(len(n) for n in NOTES)
    total_words = sum(len(n.split()) for n in NOTES)

    print(f"\n{'='*60}")
    print(f"  PILOTO v2 - Texto con tildes y pronunciacion corregida")
    print(f"{'='*60}")
    print(f"  Palabras: {total_words:,} | Caracteres: {total_chars:,}")
    print(f"  Coste estimado: ${total_chars * 0.30 / 1000:.2f}")
    print()

    # Generar audio
    print("[1/2] GENERAR AUDIO (ElevenLabs v3)")
    audio_files = []
    for i, text in enumerate(NOTES, 1):
        output_path = audio_dir / f"slide_{i:02d}.mp3"
        print(f"  [TTS]  Slide {i}/5 ({len(text)} chars)...", end=" ", flush=True)

        audio_gen = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format=OUTPUT_FORMAT,
        )

        with open(output_path, "wb") as f:
            for chunk in audio_gen:
                f.write(chunk)

        size_kb = output_path.stat().st_size // 1024
        print(f"OK ({size_kb} KB)")
        audio_files.append(output_path)
        time.sleep(1)

    # Ensamblar video
    print(f"\n[2/2] ENSAMBLAR VIDEO")
    slide_files = sorted(SLIDES_DIR.glob("slide_*.png"))[:5]
    segments_dir = OUTPUT_DIR / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)

    segment_paths = []
    total_dur = 0

    for i in range(5):
        seg_path = segments_dir / f"seg_{i+1:02d}.mp4"
        print(f"  [SEG]  {i+1}/5...", end=" ", flush=True)

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(slide_files[i]),
                "-i", str(audio_files[i]),
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-pix_fmt", "yuv420p",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
                       "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black",
                str(seg_path),
            ],
            capture_output=True,
        )

        dur = get_duration(seg_path)
        total_dur += dur
        print(f"OK ({dur:.0f}s / {dur/60:.1f}min)")
        segment_paths.append(seg_path)

    # Concatenar
    concat_file = segments_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg.resolve().as_posix()}'\n")

    video_path = OUTPUT_DIR / "piloto-v2-finops-m01.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_file), "-c", "copy", str(video_path)],
        capture_output=True,
    )

    minutes = int(total_dur // 60)
    seconds = int(total_dur % 60)
    size_mb = video_path.stat().st_size / (1024 * 1024)

    print(f"\n  {'='*50}")
    print(f"  PILOTO v2 GENERADO")
    print(f"  Video: {video_path}")
    print(f"  Slides: 5")
    print(f"  Duracion: {minutes}m {seconds}s")
    print(f"  Tamano: {size_mb:.1f} MB")
    print(f"  Media: {total_dur/5:.0f}s ({total_dur/5/60:.1f} min/slide)")
    print(f"  {'='*50}")

    # Comparar con v1
    print(f"\n  COMPARATIVA v1 vs v2:")
    v1_dir = Path("d:/09.GITHUB/formaciones/piloto/audio")
    for i in range(1, 6):
        v1 = v1_dir / f"slide_{i:02d}.mp3"
        v2 = audio_dir / f"slide_{i:02d}.mp3"
        if v1.exists():
            d1 = get_duration(v1)
            d2 = get_duration(v2)
            print(f"  Slide {i}: v1={d1:.0f}s | v2={d2:.0f}s | Diff={d2-d1:+.0f}s")


if __name__ == "__main__":
    main()
