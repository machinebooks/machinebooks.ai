# Extraído de: LibroConsultor/cap-27-caso-tecnologia.md
import anthropic
import json
from pathlib import Path

client = anthropic.Anthropic()

def analizar_estructura_servicio(nombre_servicio: str, metadatos: dict) -> dict:
    """Analiza la estructura de un servicio a partir de sus metadatos."""
    prompt = f"""Eres un arquitecto de software senior evaluando un servicio
para un proyecto de modernización.

Servicio: {nombre_servicio}
Lenguaje: {metadatos['lenguaje']}
Líneas de código: {metadatos['loc']}
Dependencias externas: {json.dumps(metadatos['dependencias'], indent=2)}
Esquema de base de datos (tablas y relaciones): {json.dumps(metadatos['esquema_db'], indent=2)}
Métricas de calidad (SonarQube): {json.dumps(metadatos['sonar'], indent=2)}

Evalúa:
1. Nivel de acoplamiento con otros servicios (alto/medio/bajo) y evidencia
2. Deuda técnica crítica (que bloquearía una migración)
3. Complejidad de migración estimada (1-5, donde 5 es máxima)
4. Dependencias que requieren sustitución en una arquitectura cloud-native
5. Riesgos específicos de este servicio durante la migración

Responde en JSON estructurado."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(message.content[0].text)

# Procesamos los 12 servicios
resultados = {}
for servicio in servicios_cliente:
    metadatos = extraer_metadatos(servicio)  # Función que extrae sin código fuente
    resultados[servicio['nombre']] = analizar_estructura_servicio(
        servicio['nombre'], metadatos
    )
