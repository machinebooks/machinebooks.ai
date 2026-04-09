# Extraido de: LibroAISafety/cap-13-prompt-injection.md
# Ejemplo didáctico de detector de prompt injection en input
# Este código ilustra el concepto — un detector de producción
# requiere un clasificador entrenado, no reglas estáticas

import re
from dataclasses import dataclass

@dataclass
class InjectionAnalysis:
    is_suspicious: bool
    confidence: float        # 0.0-1.0
    patterns_matched: list[str]
    recommendation: str      # "block", "flag", "allow"

def analizar_input(texto: str) -> InjectionAnalysis:
    """
    Análisis básico de patrones de inyección.
    Un sistema de producción usaría un clasificador ML,
    no reglas regex.
    """
    patrones_sospechosos = [
        (r"ignor[ae]\s+(todas?\s+)?(las?\s+)?instrucciones",
         "override_instructions"),
        (r"(system\s*prompt|instrucciones\s+del\s+sistema)",
         "system_prompt_reference"),
        (r"(eres|actúa\s+como|pretende\s+ser)\s+un",
         "role_assignment"),
        (r"(olvida|descarta|ignora)\s+(todo|las reglas)",
         "rule_dismissal"),
    ]

    matches = []
    for patron, nombre in patrones_sospechosos:
        if re.search(patron, texto, re.IGNORECASE):
            matches.append(nombre)

    if len(matches) >= 2:
        return InjectionAnalysis(
            is_suspicious=True,
            confidence=0.7,
            patterns_matched=matches,
            recommendation="block"
        )
    elif len(matches) == 1:
        return InjectionAnalysis(
            is_suspicious=True,
            confidence=0.4,
            patterns_matched=matches,
            recommendation="flag"  # Revisión humana
        )
    return InjectionAnalysis(
        is_suspicious=False,
        confidence=0.3,
        patterns_matched=[],
        recommendation="allow"
    )
