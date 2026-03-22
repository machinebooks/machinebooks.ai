# Extraído de: LibroCyberrange/cap-08-workzones.md
# Ejemplo didáctico: services/ai_workzone_advisor.py

import anthropic

client = anthropic.Anthropic()

SIZING_PROMPT = """Eres un experto en dimensionamiento de infraestructura
para ejercicios de ciberseguridad en un Cyber Range basado en Proxmox.

Dado el siguiente ejercicio, sugiere los recursos necesarios para una
workzone. Responde SOLO en JSON con este formato:
{
  "cpu_limit": <cores totales>,
  "memory_limit_mb": <MB totales>,
  "storage_limit_gb": <GB totales>,
  "vm_count": <número de VMs>,
  "vms": [
    {"name": "...", "role": "...", "cpu": N, "ram_mb": N, "disk_gb": N}
  ],
  "reasoning": "explicación breve de la estimación",
  "internet_required": true/false,
  "estimated_duration_hours": N,
  "recommended_ttl_hours": N
}

Restricciones del Cyber Range:
- Máximo 32 cores por workzone
- Máximo 65536 MB (64 GB) RAM por workzone
- Máximo 1000 GB almacenamiento por workzone
- pfSense consume 1 vCPU + 512 MB por workzone
- Cada VM en Proxmox tiene un overhead de ~256 MB

Descripción del ejercicio:
{exercise_description}
"""

async def suggest_workzone_sizing(
    exercise_description: str
) -> dict:
    """Usar Claude para sugerir dimensionamiento de workzone."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": SIZING_PROMPT.format(
                exercise_description=exercise_description
            ),
        }],
    )

    import json
    response_text = message.content[0].text
    # Extraer JSON de la respuesta
    sizing = json.loads(response_text)

    # Validar contra límites del sistema
    sizing["cpu_limit"] = min(sizing["cpu_limit"], 32)
    sizing["memory_limit_mb"] = min(sizing["memory_limit_mb"], 65536)
    sizing["storage_limit_gb"] = min(sizing["storage_limit_gb"], 1000)

    return sizing
