# Extraído de: LibroDevSecOps/cap-04-sast-inteligente.md
import json
import anthropic

client = anthropic.Anthropic()

PROMPT_TRIAJE = """Eres un ingeniero de seguridad senior. Analiza
el siguiente hallazgo SAST y el código circundante.

Hallazgo: {finding_id}
Severidad reportada: {severity}
Mensaje: {message}
Fichero: {file_path}
Línea: {line}

Código circundante (40 líneas):
