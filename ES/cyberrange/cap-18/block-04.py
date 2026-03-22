# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/hint_validator.py
import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationResult:
    is_safe: bool
    violations: List[str]
    filtered_text: Optional[str] = None  # Texto limpio si se pudo filtrar

class HintValidator:
    """
    Valida que las pistas generadas por IA no filtren
    información sensible antes de entregarlas al jugador.
    """

    # Patrones de flags conocidos
    FLAG_PATTERNS = [
        r'CYBERRANGE\{[^}]+\}',
        r'FLAG\{[^}]+\}',
        r'CTF\{[^}]+\}',
        r'flag\{[^}]+\}',
        r'[A-Fa-f0-9]{32}',        # MD5 hashes (posibles flags)
        r'[A-Fa-f0-9]{64}',        # SHA256 hashes
    ]

    # Patrones que indican que el modelo está dando la solución
    SOLUTION_PATTERNS = [
        r'ejecuta\s+(exactamente\s+)?[`"\'].*[`"\']',   # "ejecuta 'comando'"
        r'el\s+comando\s+es\s*:',                         # "el comando es:"
        r'la\s+(respuesta|solución|flag)\s+(es|está)',    # "la respuesta es"
        r'escribe\s+(esto|lo\s+siguiente)\s*:',           # "escribe esto:"
        r'copia\s+y\s+pega',                              # "copia y pega"
    ]

    def validate(
        self, hint_text: str, context: "PlayerContext",
        max_retries: int = 3
    ) -> ValidationResult:
        """
        Valida una pista contra patrones de filtración.
        """
        violations = []

        # Verificar patrones de flag
        for pattern in self.FLAG_PATTERNS:
            if re.search(pattern, hint_text, re.IGNORECASE):
                violations.append(f"Posible flag detectada: patrón {pattern}")

        # Verificar patrones de solución directa
        for pattern in self.SOLUTION_PATTERNS:
            if re.search(pattern, hint_text, re.IGNORECASE):
                violations.append(f"Posible solución directa: patrón {pattern}")

        # Verificar que no contiene IPs de gestión
        management_ips = ["10.0.0.1", "192.168.1.1"]  # IPs de gestión de Proxmox
        for ip in management_ips:
            if ip in hint_text:
                violations.append(f"IP de gestión detectada: {ip}")

        # Verificar longitud razonable (pistas muy largas son sospechosas)
        if len(hint_text) > 1000:
            violations.append("Pista excesivamente larga (posible volcado de información)")

        # Verificar que no menciona otros jugadores
        if re.search(r'otros?\s+(jugador|participante|equipo)', hint_text, re.IGNORECASE):
            violations.append("Referencia a otros jugadores detectada")

        return ValidationResult(
            is_safe=len(violations) == 0,
            violations=violations
        )

    def validate_with_retry(
        self, generate_fn, context: "PlayerContext",
        max_retries: int = 3
    ) -> tuple:
        """
        Intenta generar una pista válida hasta max_retries veces.
        Si todas fallan, retorna None para que se use el fallback.
        """
        for attempt in range(max_retries):
            hint_text = generate_fn()
            result = self.validate(hint_text, context)
            if result.is_safe:
                return hint_text, result
        return None, ValidationResult(
            is_safe=False,
            violations=["Máximo de reintentos alcanzado"]
        )
