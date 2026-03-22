# Extraído de: LibroDevSecOps/cap-17-aiact-pipeline.md
import anthropic
import yaml
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"

@dataclass
class ClassificationResult:
    risk_level: RiskLevel
    confidence: float          # 0.0 a 1.0
    rationale: str
    applicable_articles: list  # Artículos del AI Act aplicables
    obligations: list          # Obligaciones derivadas
    requires_human_review: bool

# Dominios del Anexo III que implican alto riesgo
ANNEX_III_DOMAINS = {
    "biometric_identification": RiskLevel.HIGH,
    "critical_infrastructure": RiskLevel.HIGH,
    "education_training": RiskLevel.HIGH,
    "employment_hr": RiskLevel.HIGH,
    "essential_services": RiskLevel.HIGH,
    "law_enforcement": RiskLevel.HIGH,
    "migration_asylum": RiskLevel.HIGH,
    "justice_democracy": RiskLevel.HIGH,
}

# Prácticas prohibidas del Art. 5
PROHIBITED_PRACTICES = [
    "social_scoring",
    "subliminal_manipulation",
    "exploitation_vulnerable",
    "real_time_biometric_public",
    "emotion_recognition_workplace",
    "untargeted_facial_scraping",
]

def classify_deterministic(manifest: dict) -> ClassificationResult | None:
    """Clasificación por reglas fijas — cubre los casos claros."""
    purpose = manifest.get("purpose", {})
    domain = purpose.get("domain", "")
    use_case = purpose.get("use_case", "")

    # Comprobar prácticas prohibidas
    for practice in PROHIBITED_PRACTICES:
        if practice in use_case.lower() or practice in domain.lower():
            return ClassificationResult(
                risk_level=RiskLevel.UNACCEPTABLE,
                confidence=0.95,
                rationale=f"El caso de uso coincide con práctica prohibida: {practice}",
                applicable_articles=["Art. 5"],
                obligations=["Prohibición total — no desplegar"],
                requires_human_review=True
            )

    # Comprobar dominios del Anexo III
    if domain in ANNEX_III_DOMAINS:
        return ClassificationResult(
            risk_level=ANNEX_III_DOMAINS[domain],
            confidence=0.90,
            rationale=f"Dominio '{domain}' listado en Anexo III del AI Act",
            applicable_articles=["Art. 6", "Art. 9-15", "Art. 43"],
            obligations=_high_risk_obligations(),
            requires_human_review=False
        )

    # Si no hay coincidencia determinista, retornar None para evaluación LLM
    return None
