# Extracted from: LibroAISafety/ch-11-red-teaming.md
# Basic structure of a red teaming harness for LLMs
# This code is didactic — it is not a functional exploit

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
    SUCCESS = "success"           # The model violates its restrictions
    PARTIAL = "partial"           # Ambiguous or partially restricted response
    FAILURE = "failure"           # The guardrail works correctly
    ERROR = "error"               # System error, not model error

@dataclass
class RedTeamAttempt:
    """Individual record of an attack attempt."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    category: AttackCategory = AttackCategory.JAILBREAK
    technique: str = ""           # Technique name (e.g., "many-shot")
    prompt: str = ""              # Exact prompt sent
    response: str = ""            # Complete model response
    classification: ResultClassification = ResultClassification.FAILURE
    confidence: float = 0.0       # 0.0-1.0: classification confidence
    notes: str = ""               # Operator observations
    model: str = ""               # Model evaluated
    temperature: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "category": self.category.value,
            "technique": self.technique,
            "prompt_length": len(self.prompt),  # Not the full prompt in logs
            "classification": self.classification.value,
            "confidence": self.confidence,
            "model": self.model,
        }
