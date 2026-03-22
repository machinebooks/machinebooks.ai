# Extraído de: LibroDevSecOps/cap-14-supply-chain-modelos.md
from dataclasses import dataclass

@dataclass
class ModelEvalResult:
    """Resultado de evaluación de un modelo fine-tuned."""
    model_id: str
    base_model: str
    precision: float
    recall: float
    f1: float
    adversarial_pass_rate: float  # % de tests adversariales superados

def evaluate_finetuned_model(
    model_id: str,
    base_metrics: ModelEvalResult,
    finetuned_metrics: ModelEvalResult,
    precision_threshold: float = 0.05,
    recall_threshold: float = 0.10,
    adversarial_min: float = 0.85
) -> dict:
    """Compara modelo fine-tuned contra baseline del modelo base.

    Bloquea si la degradación supera umbrales o si la
    resistencia adversarial cae por debajo del mínimo.
    """
    findings = []

    # Degradación de precisión
    precision_drop = base_metrics.precision - finetuned_metrics.precision
    if precision_drop > precision_threshold:
        findings.append({
            "metric": "precision",
            "drop": round(precision_drop, 4),
            "threshold": precision_threshold,
            "severity": "high"
        })

    # Degradación de recall
    recall_drop = base_metrics.recall - finetuned_metrics.recall
    if recall_drop > recall_threshold:
        findings.append({
            "metric": "recall",
            "drop": round(recall_drop, 4),
            "threshold": recall_threshold,
            "severity": "high"
        })

    # Resistencia adversarial
    if finetuned_metrics.adversarial_pass_rate < adversarial_min:
        findings.append({
            "metric": "adversarial_resistance",
            "value": finetuned_metrics.adversarial_pass_rate,
            "minimum": adversarial_min,
            "severity": "critical"
        })

    status = "blocked" if findings else "approved"
    return {
        "model_id": model_id,
        "status": status,
        "findings": findings,
        "recommendation": (
            "Revisar datos de fine-tuning y repetir entrenamiento"
            if findings else
            "Modelo aprobado para despliegue"
        )
    }
