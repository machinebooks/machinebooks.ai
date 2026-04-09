# Extraido de: LibroAISafety/cap-05-system-prompt.md
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import re

@dataclass
class ExtractionAttemptTracker:
    """
    Rastrea señales de extracción de system prompt a lo largo de una sesión.
    Acumula puntuación y alerta cuando supera el umbral.
    """
    session_id: str
    score: float = 0.0
    threshold: float = 5.0
    attempts: list[dict] = field(default_factory=list)

# Patrones que sugieren intento de extracción (con puntuación)
EXTRACTION_SIGNALS = [
    (r"(?:muestra|show|display|print).*(?:system|instruc|prompt)", 2.0),
    (r"(?:qué|what).*(?:instrucciones|instructions|rules)", 1.5),
    (r"(?:repite|repeat|copy).*(?:todo|everything|all).*(?:antes|above|before)", 3.0),
    (r"(?:actúa|act|behave).*(?:auditor|debugger|developer|admin)", 1.0),
    (r"(?:ignora|ignore|olvida|forget).*(?:anterior|previous|restricc)", 2.5),
    (r"(?:herramientas|tools|funciones|functions).*(?:disponibles|available)", 0.5),
    (r"(?:configuración|config|setup).*(?:sistema|system|internal)", 1.0),
]

def check_extraction_attempt(
    tracker: ExtractionAttemptTracker,
    user_message: str
) -> Optional[str]:
    """
    Evalúa si un mensaje contribuye a un patrón de extracción.
    Retorna alerta si la puntuación acumulada supera el umbral.
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
            f"ALERTA: sesión {tracker.session_id} — puntuación de extracción "
            f"{tracker.score:.1f} (umbral: {tracker.threshold}). "
            f"Intentos detectados: {len(tracker.attempts)}"
        )
    return None
