#!/usr/bin/env python3
"""
PILOTO: 5 slides con narracion profesional larga (~3 min/slide).
Genera audio con ElevenLabs y ensambla video de prueba.

Uso:
    python piloto_narration.py

Valida tono, ritmo y duracion antes de producir el modulo completo.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    sys.exit("ERROR: ELEVENLABS_API_KEY no configurada en .env")

VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"

# Directorio de slides exportados de Gamma
SLIDES_DIR = Path("d:/09.GITHUB/formaciones/La-Factura-que-Nadie-Esperaba/slides")
OUTPUT_DIR = Path("d:/09.GITHUB/formaciones/piloto")

# ============================================================================
# NARRACION PROFESIONAL - Estilo clase magistral
# Cada nota: 400-600 palabras = ~3 minutos de narracion natural
# Contenido extraido directamente de los capitulos 1-3 del libro
# ============================================================================

PILOTO_NOTES = [
    # SLIDE 1 - PORTADA (intro extendida del curso)
    """Bienvenidos al primer modulo del curso El FinOps Engineer y la Maquina. Mi nombre es C.P. Sylvar y durante las proximas cuatro horas vamos a explorar un problema que afecta a todas las organizaciones que han desplegado inteligencia artificial en produccion: el coste.

No hablo de un coste teorico. Hablo de facturas reales. De ese correo que llega un martes a las nueve de la manana con asunto escueto: factura API Anthropic, marzo. Y la cifra triplica la prevision trimestral. En menos de una hora, tres preguntas aterrizan en el canal de Slack del equipo de ingenieria. Primera: que equipo o servicio consumio cada bloque de tokens. Segunda: por que este mes cuesta el doble que el anterior, si no hemos lanzado funcionalidad nueva. Tercera: estamos pagando por modelos o pipelines que ya no usa nadie.

Nadie tiene respuesta para ninguna de las tres. Y ese es el punto de partida de este curso.

Este modulo se llama La Factura que Nadie Esperaba, y lo estructuramos en tres bloques. Primero, vamos a entender la anatomia del problema: por que el coste de la inteligencia artificial es tan dificil de gobernar y por que las herramientas tradicionales de FinOps no cubren este escenario. Segundo, vamos a analizar los datos reales de un caso de estudio, con facturas medidas, perfiles de consumo reales y las decisiones que tomamos para gobernarlos. Y tercero, vamos a escribir nuestras primeras lineas de codigo para calcular, registrar y visualizar costes de llamadas a modelos de lenguaje.

Si trabajan como FinOps Engineers, Cloud Architects, Engineering Managers o CTOs, este modulo les dara el marco conceptual y las herramientas practicas para entender de donde viene cada euro de su factura de inteligencia artificial. Y lo que es mas importante: les dara la capacidad de actuar sobre ese coste antes de que se descontrole.

Empecemos.""",

    # SLIDE 2 - EL PROBLEMA ($47.000)
    """Cuarenta y siete mil dolares. Esa es la cifra que aparece en la pantalla. Una factura de cloud que nadie presupuesto. El CFO quiere una explicacion para el jueves. Y tu, como responsable tecnico, no sabes si el coste viene de los tokens del modelo de lenguaje, de las instancias de GPU, del almacenamiento vectorial, o de todo a la vez.

Este escenario no es hipotetico. Es exactamente lo que ocurre cuando una organizacion despliega inteligencia artificial sin gobernanza de costes. Y la progresion siempre sigue el mismo patron.

El primer mes, la factura es baja. El equipo esta en fase de prototipo, con pocos usuarios y prompts cortos. La cifra se diluye en la partida general de cloud. Nadie la mira. El segundo mes, el producto pasa a produccion. Cincuenta usuarios empiezan a generar consultas reales. El consumo de tokens se multiplica por ocho, pero la factura tarda treinta dias en llegar. Cuando la ves, ya es historia. El tercer mes, alguien activa un agente autonomo que encadena llamadas para analisis documental. El consumo se dispara un trescientos por ciento en una semana. El cuarto mes llega la factura consolidada del trimestre. El CFO convoca una reunion de urgencia.

Un estudio de Andreessen Horowitz sobre startups con inteligencia artificial en produccion estimo que el coste de inferencia representa entre el veinte y el cuarenta por ciento del coste de los bienes vendidos de companias con productos basados en modelos generativos. Para una startup que factura cien mil euros al mes, eso implica entre veinte mil y cuarenta mil euros solo en llamadas a modelos. Sin contar infraestructura.

En entornos enterprise, el patron es distinto pero igual de danino. Cada departamento adopta IA a su ritmo. Marketing contrata una herramienta de generacion de contenido. Legal activa un servicio de analisis de contratos. Ingenieria despliega agentes de asistencia al desarrollo. Cada uno negocia su propia API key con su propio proveedor. El resultado: seis facturas de IA distintas que nadie consolida, seis patrones de consumo que nadie compara, y un gasto total que supera el presupuesto de infraestructura cloud sin que ningun equipo individual lo perciba.

El coste de no gobernar no es solo financiero. Es un coste de oportunidad. Sin datos de consumo, la organizacion no puede responder preguntas estrategicas. Que funcionalidad de IA aporta mas valor por euro invertido. Deberiamos invertir mas en el agente de analisis de riesgos o en el chatbot de soporte. Cuanto nos costaria escalar el servicio a quinientos usuarios. Sin gobernanza, cada decision de inversion en IA es una apuesta. Y las apuestas, en entornos corporativos, suelen acabar con alguien pidiendo que se apague todo.""",

    # SLIDE 3 - DOS EJES DEL COSTE
    """Este curso tiene un planteamiento que lo diferencia de cualquier otro material sobre FinOps. No hablamos solo de gobernar el coste de la inteligencia artificial. No hablamos solo de optimizar cloud con IA. Hablamos de los dos ejes a la vez, porque en la practica se cruzan de formas que la mayoria de los frameworks no contemplan.

El eje A es FinOps para IA. Gobernar el coste de tokens, modelos, pipelines RAG, agentes autonomos y herramientas MCP. Saber cuanto cuesta cada funcionalidad de IA en produccion. Asignar ese coste a equipos, productos o clientes. Detectar anomalias. Establecer politicas de seleccion de modelo segun la tarea. Implementar circuit breakers de coste que impidan que un agente desbocado genere una factura de cinco cifras en una noche.

El eje B es Cloud FinOps con IA. Construir agentes inteligentes que analicen el gasto cloud, detecten waste, recomienden optimizaciones y, en algunos casos, las ejecuten de forma autonoma. Usar Claude Agent SDK y Claude Code para crear herramientas que lean Cost Explorer, identifiquen recursos infrautilizados, propongan rightsizing y generen informes ejecutivos.

Lo interesante ocurre donde los dos ejes se cruzan. El agente de optimizacion cloud del eje B consume tokens que necesitan la gobernanza del eje A. La infraestructura que soporta los modelos de IA del eje A necesita la optimizacion del eje B. No son dos disciplinas separadas. Son dos caras del mismo problema.

Pongamos un ejemplo concreto. Imagina que construyes un agente con Claude Agent SDK que cada manana consulta el Cost Explorer de AWS, identifica instancias sobredimensionadas y envia un informe al equipo de infraestructura. Ese agente te ahorra quinientos dolares al mes en instancias. Fantastico. Pero el agente en si consume tokens: cada llamada a Claude para analizar los datos, cada invocacion de tool use para consultar las APIs de AWS, cada generacion del informe final. Si no mides el coste del agente, no sabes si tu herramienta de ahorro es rentable.

En nuestro caso real, un agente de analisis de costes cloud consume entre dos y cuatro dolares al mes en tokens. Ahorra entre trescientos y quinientos dolares. El ROI es claro. Pero sin medicion, ese dato no existe. Y sin ese dato, el CFO tiene todo el derecho a preguntar: estamos gastando dinero en IA para ahorrar dinero en cloud, y cuanto nos cuesta exactamente ese ahorro.

A lo largo de los diez modulos de este curso, construiremos ambos ejes. Con codigo real. Con decisiones documentadas y sus alternativas descartadas. Con las facturas reales que motivaron cada decision. Y con la honestidad de explicar que funciono, que no, y que todavia no sabemos resolver.""",

    # SLIDE 4 - ANATOMIA DEL COSTE LLM
    """Vamos a entrar en la parte tecnica. Para gobernar el coste de un modelo de lenguaje, primero hay que entender su anatomia. Y el primer concepto que cambia la forma de ver una factura de LLM es la asimetria de precios entre tokens de entrada y tokens de salida.

Los modelos no cobran lo mismo por leer que por generar. Para claude-sonnet-4-6, el precio es de tres dolares por millon de tokens de entrada y quince dolares por millon de tokens de salida. La ratio es uno a cinco. Esto significa que un sistema que genera respuestas largas paga cinco veces mas por token de salida que por token de entrada.

Veamos el contraste con numeros concretos. Una tarea de clasificacion de documentos usa ochocientos tokens de entrada y genera cinco tokens de salida: una etiqueta. Con claude-haiku-4-5, el coste por clasificacion es cero coma cero cero cero cero seis seis dolares. Practicamente gratis. Una tarea de generacion de informe usa tres mil tokens de entrada y genera cuatro mil de salida. Con el mismo modelo, el coste es cero coma cero uno ocho dolares. Doscientas setenta y nueve veces mas cara. Si el equipo trata ambas tareas como llamadas a LLM sin distinguir el perfil de entrada y salida, las decisiones de presupuesto seran erroneas. Diez mil clasificaciones al mes cuestan sesenta y seis centavos. Diez mil informes cuestan ciento ochenta y cuatro dolares.

Hay un tercer tipo de token que modifica este calculo: los tokens cacheados. Cuando una llamada reutiliza un prefijo de contexto que ya fue procesado, el proveedor cobra ese prefijo a precio reducido. Anthropic aplica un descuento del noventa por ciento sobre los tokens de entrada cacheados: treinta centavos por millon en lugar de tres dolares. Para sistemas con prompts de sistema extensos que se repiten en cada llamada, la diferencia entre activar o no la cache puede representar entre el cuarenta y el setenta por ciento del coste mensual de entrada.

Les cuento un caso real. En la Plataforma, el servicio de analisis normativo regeneraba el bloque de instrucciones en cada llamada porque el prompt de sistema variaba ligeramente segun el idioma del documento. Una variacion de dos caracteres en el prefijo anulaba la cache. Tres dias de analisis a pleno rendimiento con cache desactivada. Trescientos doce euros en un pico que nadie entendio hasta que alguien reviso los logs token por token.

El contraejemplo es igual de instructivo. Otro equipo descubrio que su cache de prompts funcionaba demasiado bien. El prompt de sistema cacheado tenia instrucciones desactualizadas. Durante dos semanas, el modelo respondio con un comportamiento obsoleto a un coste reducido. Ahorrar en tokens no sirve de nada si las respuestas son incorrectas. La cache exige disciplina de invalidacion: saber cuando borrarla es tan importante como saber cuando activarla.

Estos son los detalles que marcan la diferencia entre un equipo que dice gastamos tanto en IA y un equipo que dice gastamos tanto en IA, sabemos exactamente por que, y podemos optimizarlo.""",

    # SLIDE 5 - PRICING ATOMICO POR MODELO
    """Ahora que entendemos la estructura de tokens, veamos los numeros concretos. En la pantalla tienen la tabla de precios por modelo. Quiero que se fijen en la diferencia de coste entre modelos, porque esta tabla es la base de una de las decisiones de optimizacion mas potentes que veremos en este curso: el routing inteligente de modelos.

claude-opus-4-6, el modelo mas capaz de Anthropic, cuesta quince dolares por millon de tokens de entrada y setenta y cinco dolares por millon de salida. Es el modelo que usas cuando necesitas razonamiento complejo, analisis multi-paso, o generacion de alta calidad. Pero no todas las tareas lo necesitan.

claude-sonnet-4-6 cuesta tres dolares por millon de entrada y quince de salida. Es cinco veces mas barato que Opus. Para la mayoria de tareas de produccion, el analisis de documentos, la generacion de informes estandar, la respuesta a preguntas con contexto, Sonnet ofrece una calidad muy cercana a Opus a una quinta parte del precio.

claude-haiku-4-5 cuesta ochenta centavos de entrada y cuatro dolares de salida. Es casi veinte veces mas barato que Opus. Para tareas simples como clasificacion, extraccion de entidades, validacion de formato o respuestas cortas, Haiku es mas que suficiente.

La pregunta que debe hacerse todo equipo es: que porcentaje de nuestras llamadas realmente necesita el modelo mas caro. En nuestro caso, cuando analizamos el patron de uso de la Plataforma, descubrimos que el sesenta y ocho por ciento de las llamadas eran tareas que Haiku podia resolver con la misma calidad que Sonnet. Un doce por ciento eran tareas que requerian Sonnet. Y solo un veinte por ciento necesitaba la capacidad de Opus.

Antes de implementar routing de modelos, todas las llamadas iban a Sonnet. El coste mensual era de cuatrocientos treinta y nueve dolares. Despues de implementar un router que selecciona el modelo segun la complejidad de la tarea, el coste bajo a ciento ochenta y dos dolares. Una reduccion del sesenta por ciento. Sin degradar la calidad percibida por el usuario.

Pero ojo, el routing no es gratis en terminos de complejidad. Necesitas un clasificador de tareas. Necesitas definir criterios de cuando usar cada modelo. Necesitas monitorizar la calidad de las respuestas para asegurarte de que Haiku no esta fallando en tareas que deberian ir a Sonnet. Y necesitas medir el coste del propio router, que a su vez consume tokens.

Estos son los trade-offs reales de los que hablaremos en profundidad en el modulo tres. Por ahora, lo importante es que interioricen esta tabla de precios. Porque cada decision de diseno, cada prompt, cada agente que construyan, tiene un coste atomico que se deriva directamente de estos numeros. Y gobernar ese coste empieza por conocerlo.

En el siguiente bloque vamos a ver como se suman estos costes atomicos para formar la factura total, incluyendo los costes invisibles que la mayoria de los equipos ni siquiera saben que estan pagando.""",
]


def generate_audio(notes: list[str], output_dir: Path) -> list[Path]:
    from elevenlabs.client import ElevenLabs

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
        time.sleep(1)

    return audio_files


def get_duration(file_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(file_path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def build_video(slides_dir: Path, audio_dir: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    segments_dir = output_path.parent / "segments"
    segments_dir.mkdir(exist_ok=True)

    slide_files = sorted(slides_dir.glob("slide_*.png"))[:5]
    audio_files = sorted(audio_dir.glob("slide_*.mp3"))[:5]

    n = min(len(slide_files), len(audio_files))
    if n == 0:
        sys.exit("ERROR: No hay slides o audios")

    segment_paths = []
    total_duration = 0

    for i in range(n):
        seg_path = segments_dir / f"seg_{i+1:02d}.mp4"
        print(f"  [SEG]  {i+1}/{n}: {slide_files[i].name} + {audio_files[i].name}...", end=" ", flush=True)

        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(slide_files[i]),
                "-i", str(audio_files[i]),
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-pix_fmt", "yuv420p",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black",
                str(seg_path),
            ],
            capture_output=True, text=True,
        )

        if result.returncode != 0:
            print(f"FAIL")
            continue

        dur = get_duration(seg_path)
        total_duration += dur
        print(f"OK ({dur:.0f}s / {dur/60:.1f}min)")
        segment_paths.append(seg_path)

    # Concatenar
    concat_file = segments_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg.resolve().as_posix()}'\n")

    print(f"\n  [MUX]  Concatenando {len(segment_paths)} segmentos...")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_file), "-c", "copy", str(output_path)],
        capture_output=True, text=True,
    )

    minutes = int(total_duration // 60)
    seconds = int(total_duration % 60)
    size_mb = output_path.stat().st_size / (1024 * 1024)

    print(f"\n  {'='*50}")
    print(f"  PILOTO GENERADO")
    print(f"  Video: {output_path}")
    print(f"  Slides: {len(segment_paths)}")
    print(f"  Duracion: {minutes}m {seconds}s")
    print(f"  Tamano: {size_mb:.1f} MB")
    print(f"  Media por slide: {total_duration/len(segment_paths):.0f}s ({total_duration/len(segment_paths)/60:.1f}min)")
    print(f"  {'='*50}")
    print(f"\n  Objetivo: ~3 min/slide = ~15 min total para 5 slides")
    print(f"  Si el ritmo es correcto, el modulo completo de 60-80 slides = ~4h\n")


def main():
    print(f"\n{'='*60}")
    print(f"  PILOTO SYLVARSEC - 5 SLIDES NARRACION PROFESIONAL")
    print(f"{'='*60}")

    # Verificar slides
    if not SLIDES_DIR.exists():
        sys.exit(f"ERROR: No existe {SLIDES_DIR}\nExporta las slides de Gamma como PNG primero.")

    slides = sorted(SLIDES_DIR.glob("slide_*.png"))
    if len(slides) < 5:
        sys.exit(f"ERROR: Solo hay {len(slides)} slides, necesito al menos 5")

    print(f"\n  Slides: {SLIDES_DIR} ({len(slides)} disponibles, usando 5)")

    # Stats de narracion
    total_chars = sum(len(n) for n in PILOTO_NOTES)
    total_words = sum(len(n.split()) for n in PILOTO_NOTES)
    cost = total_chars * 0.30 / 1000
    print(f"  Palabras totales: {total_words:,} (~{total_words//150} min narracion)")
    print(f"  Caracteres: {total_chars:,}")
    print(f"  Coste ElevenLabs estimado: ${cost:.2f}")

    # Generar audio
    audio_dir = OUTPUT_DIR / "audio"
    print(f"\n[1/2] GENERAR AUDIO")
    generate_audio(PILOTO_NOTES, audio_dir)

    # Ensamblar video
    video_path = OUTPUT_DIR / "piloto-finops-m01.mp4"
    print(f"\n[2/2] ENSAMBLAR VIDEO")
    build_video(SLIDES_DIR, audio_dir, video_path)


if __name__ == "__main__":
    main()
