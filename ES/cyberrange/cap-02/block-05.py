# Extraído de: LibroCyberrange/cap-02-ciberejercicios.md
# Ejemplo didáctico: generación de escenarios de ciberejercicio con Claude
# Fichero: patrones/ia/exercise_generator.py

import anthropic
import json
from typing import Optional

client = anthropic.Anthropic()

EXERCISE_GENERATOR_SYSTEM = """Eres un diseñador experto de ciberejercicios con
experiencia en entornos militares (NATO Locked Shields, Cyber Coalition) y
corporativos. Tu trabajo es generar escenarios completos de ciberejercicio que
incluyan:

1. Topología de red con VMs, redes y servicios
2. Vulnerabilidades realistas mapeadas a MITRE ATT&CK
3. Retos con dificultad progresiva y flags verificables
4. Cronograma de inyecciones para el facilitador
5. Criterios de evaluación con umbrales medibles

Reglas:
- Las vulnerabilidades deben ser técnicamente realistas (CVEs reales o
  configuraciones erróneas conocidas)
- La dificultad debe ser progresiva: las primeras técnicas son detectables
  con herramientas estándar, las últimas requieren investigación manual
- Incluir siempre una dimensión de comunicación de crisis, no solo técnica
- Mapear cada reto a tácticas y técnicas MITRE ATT&CK específicas
- El output debe ser JSON válido compatible con el formato de escenario
  de la plataforma"""


def generate_exercise_scenario(
    description: str,
    exercise_type: str = "hybrid",
    difficulty: str = "intermediate",
    duration_hours: int = 8,
    num_teams: int = 4,
    include_ot: bool = False,
) -> dict:
    """
    Genera un escenario completo de ciberejercicio a partir
    de una descripción en lenguaje natural.

    Args:
        description: Descripción del ejercicio deseado
        exercise_type: tabletop | live_fire | hybrid | purple_team
        difficulty: beginner | intermediate | advanced | expert
        duration_hours: Duración prevista del ejercicio
        num_teams: Número de equipos participantes
        include_ot: Si incluir componentes OT/IoT en el escenario

    Returns:
        Diccionario con la configuración completa del escenario
    """
    prompt = f"""Genera un escenario de ciberejercicio con estas características:

- Descripción: {description}
- Tipo: {exercise_type}
- Dificultad: {difficulty}
- Duración: {duration_hours} horas
- Equipos: {num_teams}
- Incluir OT/IoT: {"sí" if include_ot else "no"}

Genera el JSON completo del escenario siguiendo el formato de la plataforma,
incluyendo: exercise, objectives, topology (networks + vms), injects y scoring.

Responde SOLO con el JSON, sin explicaciones adicionales."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=EXERCISE_GENERATOR_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parsear y validar el JSON generado
    scenario_json = json.loads(response.content[0].text)

    # Validación básica: ¿tiene las secciones obligatorias?
    required_keys = ["exercise", "objectives", "topology", "scoring"]
    for key in required_keys:
        if key not in scenario_json:
            raise ValueError(
                f"El escenario generado no incluye la sección '{key}'. "
                f"Regenerando con instrucciones más específicas."
            )

    return scenario_json


# Uso: el organizador describe lo que necesita en lenguaje natural
scenario = generate_exercise_scenario(
    description=(
        "Ejercicio de respuesta a incidente en entorno hospitalario. "
        "El adversario compromete un sistema de historiales clínicos "
        "y amenaza con publicar datos de pacientes. Incluir dimensión "
        "de protección de datos (RGPD) y comunicación con regulador."
    ),
    exercise_type="hybrid",
    difficulty="advanced",
    duration_hours=6,
    num_teams=3,
    include_ot=True,  # Equipamiento médico conectado
)
