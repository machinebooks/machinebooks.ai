# Extracted from: LibroAISafety/ch-05-system-prompt.md
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import re

@dataclass
class ExtractionAttemptTracker:
    """
    Tracks system prompt extraction signals throughout a session.
    Accumulates score and alerts when it exceeds the threshold.
    """
    session_id: str
    score: float = 0.0
    threshold: float = 5.0
    attempts: list[dict] = field(default_factory=list)

# Patterns suggesting extraction attempt (with score)
EXTRACTION_SIGNALS = [
    (r"(?:show|display|print|reveal).*(?:system|instruc|prompt)", 2.0),
    (r"(?:what).*(?:instructions|rules|guidelines)", 1.5),
    (r"(?:repeat|copy).*(?:everything|all).*(?:above|before)", 3.0),
    (r"(?:act|behave).*(?:auditor|debugger|developer|admin)", 1.0),
    (r"(?:ignore|forget|disregard).*(?:previous|prior|restricc)", 2.5),
    (r"(?:tools|functions).*(?:available|access)", 0.5),
    (r"(?:config|setup|configuration).*(?:system|internal)", 1.0),
]

def check_extraction_attempt(
    tracker: ExtractionAttemptTracker,
    user_message: str
) -> Optional[str]:
    """
    Evaluates if a message contributes to an extraction pattern.
    Returns alert if cumulative score exceeds threshold.
    """
    normalized = user_message.lower()

    for pattern, weight in EXTRACTION_SIGNALS:
        if re.search(pattern, normalized):
            tracker.score += weight
            tracker.attempts.append({
                "timestamp": datetime.now().isoformat(),
                "pattern": pattern[:40],
                "score_added": weight,
                "cumulative": tracker.score
            })

    if tracker.score >= tracker.threshold:
        return (
            f"ALERT: session {tracker.session_id} — extraction score "
            f"{tracker.score:.1f} (threshold: {tracker.threshold}). "
            f"Attempts detected: {len(tracker.attempts)}"
        )
    return None
