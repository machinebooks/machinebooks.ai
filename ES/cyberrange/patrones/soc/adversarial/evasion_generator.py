# Extraído de: LibroCyberrange/cap-21-entrenar-soc.md
# Ejemplo didáctico: generador de ataque adversarial
# patrones/soc/adversarial/evasion_generator.py

import anthropic
import json
from datetime import datetime, timedelta

client = anthropic.Anthropic()

# El agente adversarial planifica la evasión del modelo
ADVERSARY_PROMPT = """Eres un agente de red team en un ejercicio de
entrenamiento de Cyber Range. Tu objetivo es evadir el modelo de
detección de exfiltración del SOC sin ser descubierto.

CONTEXTO DEL MODELO DE DETECCIÓN:
- El modelo clasifica conexiones de red como benignas o maliciosas
- Usa features: volumen de datos, destino, protocolo, hora, usuario
- Tiene alta sensibilidad a transferencias grandes a IPs externas
- Tiene menor sensibilidad a transferencias fragmentadas y lentas

TÉCNICAS DISPONIBLES (ATLAS):
1. Fragmentación temporal: dividir la exfiltración en paquetes
   pequeños distribuidos en horas
2. Mimetización de protocolo: encapsular datos en tráfico que
   parece DNS, HTTPS o actualizaciones de software legítimas
3. Canal lento: reducir la velocidad de transferencia por debajo
   del umbral de detección volumétrica
4. Ruido de cobertura: generar tráfico benigno voluminoso para
   que la exfiltración se pierda en la línea base

Planifica una secuencia de acciones que evada la detección.
Describe cada acción con su técnica ATLAS y su efecto esperado."""


def generate_evasion_plan(
    target_data_gb: float,
    available_hours: int,
    detection_model_profile: dict
) -> dict:
    """
    Genera un plan de evasión adaptativo usando Claude
    como motor de razonamiento adversarial.
    """
    context = (
        f"Datos a exfiltrar: {target_data_gb} GB\n"
        f"Ventana temporal: {available_hours} horas\n"
        f"Perfil del modelo: {json.dumps(detection_model_profile)}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=ADVERSARY_PROMPT,
        messages=[{
            "role": "user",
            "content": context
        }]
    )

    # El plan de evasión se traduce en eventos de red
    # que se inyectan en el SIEM del escenario
    return parse_evasion_plan(response.content[0].text)


def generate_degradation_sequence(
    baseline_alert_rate: int,
    target_reduction_pct: float,
    degradation_hours: int
) -> list[dict]:
    """
    Genera la secuencia de degradación gradual de alertas.

    El atacante no elimina las alertas de golpe — las reduce
    progresivamente para que el cambio sea difícil de detectar.
    Cada hora, la tasa de alertas de exfiltración baja un
    porcentaje calculado para alcanzar el objetivo en el
    tiempo especificado.
    """
    sequence = []
    current_rate = baseline_alert_rate
    reduction_per_hour = (
        baseline_alert_rate * target_reduction_pct
    ) / degradation_hours

    for hour in range(degradation_hours):
        current_rate = max(0, current_rate - reduction_per_hour)
        # Añadir variabilidad para que parezca natural
        import random
        noise = random.uniform(-0.15, 0.15) * current_rate
        effective_rate = max(0, current_rate + noise)

        sequence.append({
            "hour": hour,
            "expected_exfil_alerts": round(effective_rate),
            "other_alerts_normal": True,
            "evasion_technique_active": (
                "slow_channel" if hour < degradation_hours / 2
                else "protocol_mimicry"
            ),
            "atlas_technique": "T0015"
        })

    return sequence
