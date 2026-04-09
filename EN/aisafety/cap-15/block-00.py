# Extracted from: LibroAISafety/ch-15-sabotage-risks.md
# Basic sabotage evaluation framework
# Didactic code — not a complete evaluation tool

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class SabotageType(Enum):
    TASK_SABOTAGE = "task_sabotage"
    OVERSIGHT_UNDERMINING = "oversight_undermining"
    CAPABILITY_HIDING = "capability_hiding"

@dataclass
class SabotageEval:
    """Individual sabotage evaluation."""
    eval_id: str
    sabotage_type: SabotageType
    task_description: str
    correct_answer: str          # Verifiably correct answer
    model_answer: str            # Model's answer
    contains_subtle_error: bool  # Did the model introduce a subtle error?
    error_description: Optional[str] = None
    human_detected: Optional[bool] = None  # Did a human reviewer detect the error?

@dataclass
class SabotageTestSuite:
    """Sabotage test suite for a domain."""
    domain: str                  # e.g., "code_review", "data_analysis"
    evaluations: list[SabotageEval]

    def detection_rate(self) -> float:
        """Human detection rate of subtle errors."""
        errors = [e for e in self.evaluations if e.contains_subtle_error]
        if not errors:
            return 1.0
        detected = sum(1 for e in errors if e.human_detected)
        return detected / len(errors)

    def sabotage_rate(self) -> float:
        """Rate of responses with subtle errors."""
        if not self.evaluations:
            return 0.0
        errors = sum(1 for e in self.evaluations if e.contains_subtle_error)
        return errors / len(self.evaluations)
