# Extraído de: LibroDevSecOps/cap-27-caso-plataforma-ia.md
import re
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"

@dataclass
class InputAnalysis:
    risk_level: RiskLevel
    flags: list[str]
    sanitized_input: str

# Patrones conocidos de inyección directa
INJECTION_PATTERNS = [
    r"ignor[ae]\s+(tus|las|todas)\s+instrucciones",
    r"olvida\s+(tus|las)\s+(reglas|instrucciones)",
    r"act[uú]a\s+como\s+(si|un)",
    r"system\s*prompt",
    r"(eres|ahora\s+eres)\s+un",
    r"<\|?(system|endoftext|im_start)\|?>",
    r"