# Extraído de: LibroCyberrange/cap-13-escenarios-topologias.md
# backend/services/scenario_ai_assistant.py
import anthropic
from typing import Dict, List

client = anthropic.Anthropic()


async def generate_scenario_description(
    topology_json: Dict,
    target_audience: str = "blue_team",
    difficulty: str = "intermediate"
) -> Dict:
    """Genera storyline, objetivos y criterios de evaluación
    a partir de una topología JSON."""

    prompt = f"""Analiza esta topología de Cyber Range y genera:
1. Una storyline realista (3-4 frases) para un ejercicio de {target_audience}
   con dificultad {difficulty}
2. 5-8 objetivos específicos y medibles
3. Criterios de evaluación con pesos (deben sumar 100)

Topología:
{json.dumps(topology_json, indent=2)}

Responde en JSON con las claves: storyline, objectives, evaluation_criteria.
El storyline debe ser en español y describir un incidente realista
que motive el ejercicio."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(message.content[0].text)


async def suggest_vm_templates(
    training_objective: str,
    max_vms: int = 15
) -> List[Dict]:
    """Sugiere configuraciones de VM para un objetivo de entrenamiento."""

    prompt = f"""Como experto en Cyber Ranges, sugiere las VMs necesarias
para este objetivo de entrenamiento:

Objetivo: {training_objective}
Máximo de VMs: {max_vms}

Para cada VM indica:
- name: nombre descriptivo
- os: sistema operativo
- type: server/workstation/firewall/plc/sensor
- services: lista de servicios a instalar
- vulnerabilities: vulnerabilidades a inyectar (si aplica)
- network_zone: zona de red donde ubicarla
- cpu: cores necesarios
- memory_mb: RAM necesaria

Responde en JSON (lista de objetos VM). Prioriza escenarios
realistas sobre escenarios con muchas VMs."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(message.content[0].text)
