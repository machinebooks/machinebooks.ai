# Extraido de: LibroAISafety/cap-12-jailbreaking.md
# Estructura de una batería de tests de evasión
# Código didáctico — NO contiene prompts adversariales reales

from dataclasses import dataclass
from enum import Enum
from typing import Callable

class JailbreakClass(Enum):
    ROLE_PLAY = "identity_manipulation"
    ENCODING = "encoding_obfuscation"
    CRESCENDO = "gradual_escalation"
    CONTEXT_MANIPULATION = "context_flooding"
    FORMAT_EXPLOIT = "format_exploitation"

@dataclass
class EvasionTest:
    """Un test individual de evasión."""
    test_id: str
    jailbreak_class: JailbreakClass
    description: str
    # El prompt NO se hardcodea — se genera por el operador
    # según el contexto del sistema evaluado
    target_behavior: str          # Qué debería hacer el modelo si el jailbreak tiene éxito
    expected_defense: str         # Qué debería hacer el modelo si el guardrail funciona
    severity_if_success: str      # low / medium / high / critical
    requires_multi_turn: bool     # Si necesita más de un turno de conversación
    min_attempts: int = 10        # Mínimo de intentos para calcular reproducibilidad

@dataclass
class EvasionBattery:
    """Batería completa de tests de evasión."""
    tests: list[EvasionTest]
    target_model: str
    target_system: str            # Descripción del sistema evaluado

    def coverage_report(self) -> dict:
        """Verifica cobertura: ¿hay al menos un test por clase?"""
        covered = set(t.jailbreak_class for t in self.tests)
        missing = set(JailbreakClass) - covered
        return {
            "total_tests": len(self.tests),
            "classes_covered": len(covered),
            "classes_total": len(JailbreakClass),
            "missing": [m.value for m in missing],
            "complete": len(missing) == 0,
        }
