# Extraido de: LibroAISafety/cap-05-system-prompt.md
# Patrón de versionado de system prompts
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256

@dataclass
class SystemPromptVersion:
    """Una versión inmutable del system prompt."""
    version: str                  # Semver: "2.3.1"
    content: str                  # El prompt completo
    author: str                   # Quién hizo el cambio
    reason: str                   # Por qué se cambió
    created_at: datetime = field(default_factory=datetime.now)
    security_review: bool = False # ¿Pasó revisión de seguridad?
    tests_passed: bool = False    # ¿Pasó la batería de regresión?
    content_hash: str = ""        # Hash para verificar integridad

    def __post_init__(self):
        self.content_hash = sha256(
            self.content.encode()
        ).hexdigest()[:16]

@dataclass
class PromptRollbackManager:
    """Gestiona versiones y permite rollback rápido."""
    versions: list[SystemPromptVersion] = field(default_factory=list)
    active_version: str = ""

    def deploy(self, version: str) -> bool:
        """Despliega una versión específica como activa."""
        target = next((v for v in self.versions if v.version == version), None)
        if not target:
            return False
        if not target.security_review or not target.tests_passed:
            raise ValueError(
                f"Versión {version} no aprobada: "
                f"security={target.security_review}, "
                f"tests={target.tests_passed}"
            )
        self.active_version = version
        return True

    def rollback(self) -> str:
        """Revierte a la versión anterior aprobada."""
        approved = [v for v in self.versions
                    if v.security_review and v.tests_passed]
        if len(approved) < 2:
            raise ValueError("No hay versión anterior aprobada")
        # La penúltima versión aprobada
        previous = approved[-2]
        self.active_version = previous.version
        return previous.version
