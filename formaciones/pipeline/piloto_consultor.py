#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Piloto Consultor: 5 slides con narración profesional."""

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

OUTPUT_DIR = Path("d:/09.GITHUB/formaciones/piloto-consultor")

NOTES = [
    # SLIDE 1 — PORTADA
    (
        "Bienvenidos al módulo uno del curso El Consultor y la Máquina: "
        "La crisis silenciosa de la consultoría. Mi nombre es C. P. Sylvar "
        "y durante las próximas horas vamos a hablar de algo que la mayoría "
        "de las consultoras saben pero pocas reconocen en voz alta: el modelo "
        "tradicional de consultoría está roto.\n\n"

        "No hablo de una crisis dramática. No hay titulares de prensa. No "
        "hay despidos masivos. Es algo más sutil y más peligroso. Es una "
        "erosión lenta de márgenes, una pérdida constante de conocimiento "
        "institucional y una presión creciente de clientes que cada vez "
        "pagan menos por lo mismo. Y ahora, encima, los clientes tienen "
        "acceso a modelos de lenguaje que hacen en cuatro minutos lo que un "
        "consultor junior tardaba tres días en investigar.\n\n"

        "Este módulo nace de una experiencia concreta. Eran las once y media "
        "de la noche de un miércoles. Tres consultores llevábamos catorce "
        "días preparando una propuesta técnica para un organismo público. El "
        "documento de requisitos tenía doscientas ochenta y siete páginas. "
        "La matriz de cumplimiento, ciento sesenta y cuatro controles "
        "cruzados contra tres marcos normativos. El plazo de entrega era el "
        "viernes. Y uno de nosotros, el más senior, con quince años de "
        "experiencia en auditorías de seguridad, estaba copiando a mano los "
        "criterios de valoración del pliego a una hoja de cálculo porque el "
        "PDF no permitía extraer tablas. Llevaba dos horas en esa tarea.\n\n"

        "La propuesta se entregó a tiempo. Tres semanas después, supimos que "
        "no la habíamos ganado. No por calidad técnica. La puntuación "
        "técnica fue la segunda más alta. La ganó una consultora que ofertó "
        "un dieciocho por ciento menos en la parte económica. Ciento veinte "
        "horas de trabajo de tres profesionales. Más de catorce mil euros en "
        "coste interno. Para acabar segundos por precio.\n\n"

        "Esa noche no fue excepcional. Fue representativa. Y este curso "
        "existe porque decidimos que no podía seguir siendo la norma."
    ),

    # SLIDE 2 — LA CRISIS EN NÚMEROS
    (
        "Veamos los números que definen esta crisis. Y son números del "
        "sector, no opiniones.\n\n"

        "Los márgenes brutos de la consultoría tecnológica han pasado del "
        "treinta y cinco por ciento al quince por ciento en la última "
        "década. En diez años, los márgenes se han reducido a menos de la "
        "mitad. ¿Por qué? Porque los servicios que antes eran "
        "especializados ahora son commodities. Una auditoría de ISO 27001, "
        "un gap analysis de ENS, una evaluación de cumplimiento de RGPD. "
        "Hace diez años, pocas consultoras podían hacerlo. Hoy, docenas "
        "compiten por el mismo contrato. Y cuando hay docenas de "
        "proveedores, el precio baja.\n\n"

        "La tasa de éxito en propuestas oscila entre el quince y el treinta "
        "por ciento. Esto significa que de cada diez propuestas que "
        "preparas, ganas entre una y tres. Las otras siete u ocho son coste "
        "hundido. Con un coste medio de preparación de más de ochenta horas "
        "por propuesta compleja, estamos hablando de que una consultora "
        "mediana invierte entre quinientas y seiscientas horas al año en "
        "propuestas que no gana. Eso son entre treinta y cuarenta mil euros "
        "anuales en tiempo de profesionales cualificados que no produce "
        "retorno.\n\n"

        "La rotación de consultores senior se sitúa entre el dieciocho y "
        "el veintidós por ciento anual. Uno de cada cinco seniors se va cada "
        "año. Y cuando se van, no se va solo una persona. Se van las "
        "relaciones con el cliente, el contexto de proyectos anteriores, "
        "las lecciones aprendidas que nunca se documentaron y el criterio "
        "para saber cuándo un hallazgo de auditoría es una observación menor "
        "y cuándo es una bomba de relojería. Ese conocimiento no está en "
        "ningún sistema. Está en la cabeza del consultor. Y cuando esa "
        "cabeza se va, el siguiente proyecto arranca casi desde cero.\n\n"

        "Y hay un dato más que cierra el cuadro. McKinsey estimó en dos mil "
        "veinticuatro que entre el cuarenta y el sesenta por ciento de las "
        "actividades de consultoría de gestión son susceptibles de "
        "automatización con inteligencia artificial generativa. No el "
        "cuarenta por ciento de los consultores. El cuarenta por ciento de "
        "las actividades. La diferencia es crucial: no se trata de sustituir "
        "personas, se trata de liberar a esas personas del trabajo mecánico "
        "para que hagan el trabajo que realmente aporta valor."
    ),

    # SLIDE 3 — LA COMMODITIZACIÓN
    (
        "Vamos a hablar del elefante en la habitación. La commoditización "
        "del conocimiento técnico accesible.\n\n"

        "Lo que un consultor junior tardaba tres días en investigar, "
        "qué dice la ISO 27001 sobre gestión de accesos, cómo se estructura "
        "un gap analysis del Esquema Nacional de Seguridad, qué patrones de "
        "arquitectura cloud recomienda el proveedor para cargas "
        "transaccionales, hoy lo responde un modelo de lenguaje en cuatro "
        "minutos. No con la profundidad de un especialista con quince años "
        "de experiencia. Pero sí con la suficiente calidad para que un "
        "director de tecnología se pregunte: ¿por qué estoy pagando ciento "
        "cincuenta euros la hora por algo que una inteligencia artificial "
        "hace gratis?\n\n"

        "Esa pregunta, que ya escuchamos en tres reuniones comerciales solo "
        "en el último trimestre de dos mil veinticinco, no es injusta. Es "
        "incómoda, pero legítima. Y merece una respuesta honesta en lugar "
        "de una defensa corporativa.\n\n"

        "La respuesta honesta tiene dos partes. La primera: sí, una parte "
        "significativa del trabajo que factura una consultora es trabajo de "
        "recopilación, estructuración y redacción que los modelos de "
        "lenguaje realizan de forma competente. La segunda: el valor real de "
        "un consultor experimentado no está en recopilar información ni en "
        "redactar informes. Está en saber qué información buscar, qué "
        "preguntas hacer al cliente que el cliente no se ha hecho a sí "
        "mismo, y qué recomendar cuando los datos son ambiguos y las "
        "consecuencias irreversibles.\n\n"

        "El problema es que el modelo de negocio de la consultoría no "
        "distingue entre ambos tipos de trabajo. Cobra por hora, no por "
        "decisión. Y cuando cobras por hora, cualquier tecnología que "
        "reduzca horas reduce ingresos. Eso crea un incentivo perverso: la "
        "consultora que adopta inteligencia artificial internamente se "
        "vuelve más productiva pero factura menos, salvo que cambie su "
        "modelo de pricing. La que no la adopta mantiene la facturación "
        "pero pierde competitividad frente a quien sí lo ha hecho.\n\n"

        "Esta trampa estructural es la crisis silenciosa. No es un problema "
        "de talento. Es un problema de modelo. Y la salida no es trabajar "
        "más horas. Es cambiar lo que vendes."
    ),

    # SLIDE 4 — LA DECISIÓN: TRES CAMINOS
    (
        "Cuando nos enfrentamos a esta realidad, y digo nos enfrentamos "
        "porque la vivimos desde dentro, no como observadores, evaluamos "
        "tres caminos posibles.\n\n"

        "El primer camino era comprar herramientas genéricas. Una "
        "suscripción empresarial a un modelo de lenguaje, veinte a "
        "cincuenta dólares por consultor al mes, y dejar que cada uno lo "
        "use como considere. Conocimos consultoras que tomaron este camino. "
        "La adopción inicial fue alta: el setenta por ciento de los "
        "consultores usaba la herramienta la primera semana. A los tres "
        "meses, el uso activo había caído al veinticinco por ciento. Los "
        "seniors dejaron de usarla porque pierde matices. Los juniors la "
        "usaban como muleta para redactar, pero sin criterio para validar "
        "si lo generado era correcto en contexto. El resultado neto fue "
        "ruido disfrazado de productividad.\n\n"

        "El segundo camino era adoptar una plataforma de consultoría con "
        "inteligencia artificial integrada. Coste: entre quinientos y dos "
        "mil euros por usuario al mes. El problema con estas plataformas es "
        "triple. Primero, son genéricas: están diseñadas para consultores "
        "en abstracto, no para una práctica de consultoría tecnológica con "
        "foco en seguridad o arquitectura. Segundo, exigen adaptar tu "
        "proceso a su flujo de trabajo, no al revés. Tercero, y este es el "
        "factor decisivo, tu conocimiento acumulado vive en su sistema, no "
        "en el tuyo. Si cambias de plataforma, pierdes el contexto. Es "
        "vendor lock-in aplicado al activo más valioso de una consultora: "
        "su base de conocimiento.\n\n"

        "El tercer camino era construir nuestro propio stack. Diseñar un "
        "conjunto de herramientas y agentes específicos para nuestra "
        "práctica de consultoría, usando las APIs de modelos de lenguaje "
        "como componente, no como producto. Coste inicial más alto. Curva "
        "de aprendizaje más pronunciada. Pero con una ventaja decisiva: el "
        "conocimiento se queda en tu infraestructura, los agentes se "
        "adaptan a tu proceso, y la inversión se acumula en lugar de "
        "evaporarse cuando cancelas una suscripción.\n\n"

        "Elegimos el tercer camino. No porque fuera lo más fácil. Fue, con "
        "diferencia, la opción que más esfuerzo inicial requirió. Sino "
        "porque era la única que nos permitía acumular conocimiento de "
        "forma compuesta. Cada propuesta que analizamos, cada auditoría que "
        "ejecutamos, cada lección que documentamos, alimenta un sistema que "
        "mejora con el uso. Las otras opciones nos convertían en "
        "consumidores de una herramienta ajena. Esta nos convertía en "
        "constructores de un activo propio."
    ),

    # SLIDE 5 — EL IMPACTO REAL
    (
        "¿Y cuál fue el resultado? Veamos los datos reales, porque en este "
        "curso no vendemos promesas. Vendemos mediciones.\n\n"

        "Propuestas técnicas complejas: de ciento veinte horas de "
        "preparación a veinte horas. Una reducción del ochenta y tres por "
        "ciento. No porque la inteligencia artificial escriba la propuesta "
        "por nosotros. Sino porque el agente de análisis de RFP extrae en "
        "quince minutos lo que antes tardábamos dos días en leer y "
        "estructurar. Porque el sistema de generación aumentada por "
        "recuperación sobre nuestras propuestas anteriores nos da un "
        "borrador contextualizado en lugar de empezar de cero. Y porque el "
        "estimador de esfuerzos consulta datos históricos reales en lugar "
        "de depender de la intuición del senior de turno.\n\n"

        "Informes de cumplimiento normativo: de tres días de trabajo a "
        "cuatro horas. El agente cruza los controles del marco normativo "
        "contra las evidencias del cliente, genera el borrador con "
        "hallazgos priorizados por impacto y riesgo, y el consultor senior "
        "dedica su tiempo a validar, matizar y añadir las recomendaciones "
        "que solo la experiencia humana puede dar.\n\n"

        "Análisis de un RFP de trescientas páginas: de dos días a quince "
        "minutos. Coste del análisis con inteligencia artificial: ochenta "
        "centavos de dólar. Coste del mismo análisis con un junior: "
        "seiscientos euros. El agente no sustituye al senior que toma la "
        "decisión de presentar o no presentar. Sustituye las ocho horas de "
        "lectura, extracción y estructuración que precedían a esa decisión.\n\n"

        "Y el dato que lo cambia todo: la base de conocimiento. Doce años "
        "de documentación de consultoría, propuestas, informes, lecciones "
        "aprendidas, indexados en un sistema de recuperación semántica. "
        "Cuando un consultor pregunta: ¿cómo resolvimos el tema de "
        "autenticación en el proyecto del organismo público en dos mil "
        "veinticuatro?, el sistema responde en tres segundos con el "
        "contexto completo. Antes, esa respuesta dependía de que el "
        "consultor que trabajó en ese proyecto siguiera en la empresa. Y "
        "con una rotación del veinte por ciento anual, había una "
        "probabilidad significativa de que ya no estuviera.\n\n"

        "Tres ideas para cerrar este módulo. Primera: la crisis de la "
        "consultoría no es de talento, es de modelo. Cobrar por hora "
        "penaliza la eficiencia. Segunda: el cincuenta y cinco por ciento "
        "del tiempo del consultor es trabajo que la inteligencia artificial "
        "puede ejecutar. Libera al senior para lo que solo el senior sabe "
        "hacer: decidir. Tercera: construir tu propio stack genera ventaja "
        "compuesta. Cada proyecto alimenta al siguiente. Y esa es la "
        "diferencia entre una consultora que sobrevive y una que prospera.\n\n"

        "En el próximo módulo desglosaremos un proyecto de consultoría "
        "real fase por fase, identificando exactamente dónde entra la "
        "inteligencia artificial y dónde el juicio humano es "
        "irremplazable. Nos vemos en el módulo dos."
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
    print(f"  PILOTO CONSULTOR - 5 slides, tema SylvarSec")
    print(f"{'='*60}")
    print(f"  Palabras: {total_words:,} | Caracteres: {total_chars:,}")
    print(f"  Coste estimado: ${total_chars * 0.30 / 1000:.2f}")
    print()

    # Generar audio
    print("[1/1] GENERAR AUDIO (ElevenLabs v3)")
    for i, text in enumerate(NOTES, 1):
        output_path = audio_dir / f"slide_{i:02d}.mp3"
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"  [SKIP] Slide {i}: ya existe")
            continue
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
        time.sleep(1)

    # Resultados
    print(f"\n  RESULTADOS:")
    print(f"  {'-'*50}")
    total_dur = 0
    for i in range(1, 6):
        f = audio_dir / f"slide_{i:02d}.mp3"
        if f.exists():
            dur = get_duration(f)
            total_dur += dur
            print(f"  Slide {i}: {int(dur//60)}m {int(dur%60)}s ({f.stat().st_size//1024} KB)")

    print(f"\n  Total: {int(total_dur//60)}m {int(total_dur%60)}s")
    print(f"  Media: {total_dur/5:.0f}s ({total_dur/5/60:.1f} min/slide)")
    print(f"  Audio: {audio_dir}")
    print(f"\n  Cuando la presentacion de Gamma este lista,")
    print(f"  exporta como PNG y ensambla el video con build_video.py")


if __name__ == "__main__":
    main()
