# Extraído de: LibroCyberrange/cap-21-entrenar-soc.md
# Ejemplo didáctico: pipeline de datos etiquetados
# patrones/soc/data_pipeline/labeled_data_exporter.py

from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class LabeledSecurityEvent:
    """
    Evento de seguridad etiquetado generado por un ejercicio
    del Cyber Range. Incluye la verdad del terreno, el contexto
    completo y las decisiones tomadas (humanas y de IA).
    """
    event_id: str
    timestamp: datetime
    # Datos del evento
    event_type: str           # alert, log, network_flow, etc.
    event_source: str         # siem, edr, firewall, ids
    raw_data: dict            # Evento original completo
    # Verdad del terreno (ground truth del escenario)
    ground_truth: str         # true_positive, false_positive, noise
    attack_technique: str | None  # MITRE ATT&CK T-code si aplica
    attack_phase: str | None      # kill_chain phase si aplica
    # Decisiones
    ai_classification: str | None
    ai_confidence: float | None
    human_classification: str | None
    human_response_time_s: float | None
    # Contexto del ejercicio
    scenario_id: str
    scenario_difficulty: str
    analyst_tier: str


def export_exercise_dataset(
    exercise_id: str,
    events: list[LabeledSecurityEvent]
) -> dict:
    """
    Exporta los datos etiquetados de un ejercicio en formato
    compatible con pipelines de entrenamiento de modelos ML.
    """
    dataset = {
        "metadata": {
            "exercise_id": exercise_id,
            "export_date": datetime.now().isoformat(),
            "total_events": len(events),
            "label_distribution": {
                "true_positive": sum(
                    1 for e in events
                    if e.ground_truth == "true_positive"
                ),
                "false_positive": sum(
                    1 for e in events
                    if e.ground_truth == "false_positive"
                ),
                "noise": sum(
                    1 for e in events
                    if e.ground_truth == "noise"
                )
            },
            "attack_techniques": list(set(
                e.attack_technique for e in events
                if e.attack_technique
            )),
            # Métricas de calidad del etiquetado
            "ai_accuracy": calculate_accuracy(events, "ai"),
            "human_accuracy": calculate_accuracy(events, "human"),
            "ai_human_agreement": calculate_agreement(events)
        },
        "events": [
            {
                "event_id": e.event_id,
                "features": extract_ml_features(e.raw_data),
                "label": e.ground_truth,
                "attack_metadata": {
                    "technique": e.attack_technique,
                    "phase": e.attack_phase
                },
                "decisions": {
                    "ai": {
                        "classification": e.ai_classification,
                        "confidence": e.ai_confidence
                    },
                    "human": {
                        "classification": e.human_classification,
                        "response_time_s": e.human_response_time_s
                    }
                }
            }
            for e in events
        ]
    }

    return dataset


def calculate_accuracy(
    events: list[LabeledSecurityEvent],
    actor: str
) -> float:
    """Calcula la precisión de clasificación de IA o humano."""
    classified = [
        e for e in events
        if getattr(e, f"{actor}_classification") is not None
    ]
    if not classified:
        return 0.0
    correct = sum(
        1 for e in classified
        if getattr(e, f"{actor}_classification") == e.ground_truth
    )
    return correct / len(classified)


def calculate_agreement(
    events: list[LabeledSecurityEvent]
) -> float:
    """Calcula el acuerdo entre clasificación IA y humana."""
    both = [
        e for e in events
        if e.ai_classification and e.human_classification
    ]
    if not both:
        return 0.0
    agreed = sum(
        1 for e in both
        if e.ai_classification == e.human_classification
    )
    return agreed / len(both)
