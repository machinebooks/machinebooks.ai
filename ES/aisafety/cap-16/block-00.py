# Extraido de: LibroAISafety/cap-16-seguridad-agentes.md
from dataclasses import dataclass, field
from typing import Any, Callable
from enum import Enum
import re
import logging

logger = logging.getLogger("agent_security")

class RiskLevel(Enum):
    LOW = "low"           # Lectura de datos, consultas
    MEDIUM = "medium"     # Modificación de datos propios
    HIGH = "high"         # Borrado, envío externo
    CRITICAL = "critical" # Acciones irreversibles en producción

@dataclass
class ToolPermission:
    """Define qué puede hacer una herramienta y bajo qué condiciones."""
    name: str
    risk_level: RiskLevel
    allowed_params: dict[str, type]      # Parámetros permitidos y sus tipos
    forbidden_patterns: list[str] = field(default_factory=list)
    requires_approval: bool = False       # True = human-in-the-loop
    max_calls_per_session: int = 100      # Rate limiting por sesión

class ToolValidator:
    """Valida invocaciones de herramientas antes de ejecutarlas."""

    def __init__(self, permissions: list[ToolPermission]):
        self._permissions = {p.name: p for p in permissions}
        self._call_counts: dict[str, int] = {}

    def validate(self, tool_name: str, params: dict[str, Any]) -> tuple[bool, str]:
        """Retorna (permitido, razón) para cada invocación."""
        perm = self._permissions.get(tool_name)
        if not perm:
            logger.warning(f"Herramienta no registrada: {tool_name}")
            return False, f"Herramienta '{tool_name}' no está en el registro"

        # Validar tipos de parámetros
        for key, value in params.items():
            expected_type = perm.allowed_params.get(key)
            if expected_type is None:
                return False, f"Parámetro '{key}' no permitido"
            if not isinstance(value, expected_type):
                return False, f"Tipo incorrecto para '{key}'"

        # Detectar patrones prohibidos (inyección SQL, comandos shell, etc.)
        param_str = str(params)
        for pattern in perm.forbidden_patterns:
            if re.search(pattern, param_str, re.IGNORECASE):
                logger.critical(
                    f"Patrón prohibido detectado en {tool_name}: {pattern}"
                )
                return False, f"Contenido prohibido detectado"

        # Rate limiting
        count = self._call_counts.get(tool_name, 0)
        if count >= perm.max_calls_per_session:
            return False, f"Límite de invocaciones alcanzado ({count})"
        self._call_counts[tool_name] = count + 1

        # Aprobación humana para herramientas de alto riesgo
        if perm.requires_approval:
            return False, "REQUIRES_APPROVAL"

        return True, "OK"
