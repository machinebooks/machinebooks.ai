# Extraido de: LibroAISafety/cap-11-red-teaming.md
# Estructura básica de un harness de red teaming para LLMs
# Este código es didáctico — no es un exploit funcional

import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class AttackCategory(Enum):
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    DATA_EXTRACTION = "data_extraction"
    GOAL_HIJACK = "goal_hijack"

class ResultClassification(Enum):
    SUCCESS = "success"           # El modelo viola sus restricciones
    PARTIAL = "partial"           # Respuesta ambigua o parcialmente restringida
    FAILURE = "failure"           # El guardrail funciona correctamente
    ERROR = "error"               # Error del sistema, no del modelo

@dataclass
class RedTeamAttempt:
    """Registro individual de un intento de ataque."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    category: AttackCategory = AttackCategory.JAILBREAK
    technique: str = ""           # Nombre de la técnica (e.g., "many-shot")
    prompt: str = ""              # Prompt exacto enviado
    response: str = ""            # Respuesta completa del modelo
    classification: ResultClassification = ResultClassification.FAILURE
    confidence: float = 0.0       # 0.0-1.0: confianza en la clasificación
    notes: str = ""               # Observaciones del operador
    model: str = ""               # Modelo evaluado
    temperature: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "category": self.category.value,
            "technique": self.technique,
            "prompt_length": len(self.prompt),  # No el prompt completo en logs
            "classification": self.classification.value,
            "confidence": self.confidence,
            "model": self.model,
        }
