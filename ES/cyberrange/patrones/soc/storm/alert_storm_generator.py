# Extraído de: LibroCyberrange/cap-21-entrenar-soc.md
# Ejemplo didáctico: generador de tormenta de alertas
# patrones/soc/storm/alert_storm_generator.py

import anthropic
import json
import random
from datetime import datetime, timedelta

client = anthropic.Anthropic()

STORM_GENERATOR_PROMPT = """Genera una alerta de seguridad
realista para un escenario de tormenta de alertas en un SOC.

CONTEXTO DEL ESCENARIO:
- Entorno empresarial con 500 endpoints, 20 servidores, 3 DMZ
- El atacante ha lanzado una operación coordinada
- Hay un ataque real mezclado con ruido deliberado
- Las alertas deben ser técnicamente precisas

TIPOS DE ALERTA DISPONIBLES:
- network_scan: escaneo de puertos (ruido del atacante)
- brute_force: intentos de autenticación (puede ser ataque real)
- malware_detection: firma detectada por EDR
- lateral_movement: movimiento lateral via SMB/WMI/PsExec
- data_exfiltration: transferencia de datos a IP externa
- privilege_escalation: elevación de privilegios
- c2_communication: comunicación con C2
- policy_violation: violación de política (ruido benigno)
- software_update: actualización legítima (falso positivo)

Genera UNA alerta con todos sus campos. Indica si es
true_positive, false_positive, o noise."""


def generate_alert_storm(
    total_alerts: int = 200,
    duration_minutes: int = 30,
    true_positive_count: int = 12,
    attack_narrative: str = "coordinated_apt"
) -> list[dict]:
    """
    Genera una tormenta de alertas con la proporción correcta
    de señal (ataques reales) y ruido (falsos positivos,
    escaneos, actividad legítima).

    Claude genera cada alerta con realismo técnico — no son
    plantillas genéricas sino alertas con IPs, puertos,
    usuarios y timestamps coherentes con el narrativo.
    """
    alerts = []
    start_time = datetime.now()
    interval = timedelta(minutes=duration_minutes) / total_alerts

    # Distribuir los verdaderos positivos en la línea temporal
    tp_positions = sorted(random.sample(
        range(total_alerts), true_positive_count
    ))

    for i in range(total_alerts):
        is_tp = i in tp_positions
        alert_time = start_time + (interval * i)

        # Claude genera alertas con realismo técnico
        response = client.messages.create(
            model="claude-haiku-4-5",  # Haiku por velocidad
            max_tokens=512,
            system=STORM_GENERATOR_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"Genera alerta #{i+1}. "
                    f"Timestamp: {alert_time.isoformat()}. "
                    f"{'DEBE ser true_positive de la cadena '
                     'de ataque APT' if is_tp else
                     'Puede ser false_positive o ruido'}. "
                    f"Narrativo: {attack_narrative}."
                )
            }]
        )

        alert = json.loads(response.content[0].text)
        alert["_meta"] = {
            "ground_truth": "true_positive" if is_tp else
                           alert.get("classification", "noise"),
            "sequence_position": i,
            "generated_at": alert_time.isoformat()
        }
        alerts.append(alert)

    return alerts


def evaluate_triage_performance(
    analyst_decisions: list[dict],
    ground_truth: list[dict],
    time_limit_minutes: int = 30
) -> dict:
    """
    Evalúa el rendimiento del analista en la tormenta de alertas.
    Calcula métricas de triaje bajo presión.
    """
    tp_detected = 0
    tp_total = sum(
        1 for a in ground_truth
        if a["_meta"]["ground_truth"] == "true_positive"
    )
    fp_escalated = 0
    total_reviewed = len(analyst_decisions)

    for decision in analyst_decisions:
        alert_id = decision["alert_id"]
        truth = next(
            a for a in ground_truth if a["id"] == alert_id
        )

        if (truth["_meta"]["ground_truth"] == "true_positive"
            and decision["action"] in ["escalate", "investigate"]):
            tp_detected += 1
        elif (truth["_meta"]["ground_truth"] != "true_positive"
              and decision["action"] == "escalate"):
            fp_escalated += 1

    detection_rate = tp_detected / tp_total if tp_total > 0 else 0
    false_escalation_rate = (
        fp_escalated / total_reviewed if total_reviewed > 0 else 0
    )

    return {
        "total_alerts": len(ground_truth),
        "alerts_reviewed": total_reviewed,
        "coverage": total_reviewed / len(ground_truth),
        "true_positives_detected": tp_detected,
        "true_positives_total": tp_total,
        "detection_rate": detection_rate,
        "false_escalations": fp_escalated,
        "false_escalation_rate": false_escalation_rate,
        # La métrica compuesta penaliza tanto los falsos
        # negativos (amenazas no detectadas) como la
        # saturación del equipo de Tier 2 (falsas escalaciones)
        "triage_score": (
            detection_rate * 0.7 -
            false_escalation_rate * 0.3
        )
    }
