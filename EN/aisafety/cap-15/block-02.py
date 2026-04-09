# Extracted from: LibroAISafety/ch-15-sabotage-risks.md
# Concept of evaluation embedded in production
# NOT an exploit — it is a defensive evaluation technique

from dataclasses import dataclass
import random

@dataclass
class EmbeddedEval:
    """Evaluation embedded in the production flow."""
    eval_id: str
    real_request: str          # Real user request
    eval_variant: str          # Evaluation variant
    expected_behavior: str     # Expected behavior
    actual_behavior: str = ""  # Filled in with the response

def should_inject_eval(probability: float = 0.01) -> bool:
    """
    Decides whether this request will include an embedded evaluation.
    Low probability to avoid affecting performance.
    """
    return random.random() < probability

def create_sabotage_eval(domain: str) -> EmbeddedEval:
    """
    Creates a domain-specific sabotage evaluation.
    The model receives a real task and it is verified
    whether the response contains deliberate subtle errors.
    """
    # Implementation depends on the domain
    # For code: send code with a known bug
    #   and verify whether the model detects it
    # For data: send a dataset with an anomaly
    #   and verify whether the model reports it
    pass
