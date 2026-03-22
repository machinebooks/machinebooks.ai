# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class FindingSource(Enum):
    SAST = "sast"          # Semgrep
    SCA = "sca"            # Grype
    CONTAINER = "container" # Trivy

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class NormalizedFinding:
    """Hallazgo normalizado de cualquier herramienta de escaneo."""
    id: str                          # Identificador único del hallazgo
    source: FindingSource            # Herramienta de origen
    severity: Severity               # Severidad original reportada
    title: str                       # Descripción breve
    cve_id: Optional[str] = None     # CVE si aplica (SCA/container)
    cwe_id: Optional[str] = None     # CWE para clasificación
    cvss_score: Optional[float] = None
    file_path: Optional[str] = None  # Fichero afectado
    line_number: Optional[int] = None
    service_name: Optional[str] = None  # Servicio al que pertenece
    package_name: Optional[str] = None  # Paquete afectado (SCA)
    package_version: Optional[str] = None
    fixed_version: Optional[str] = None # Versión que corrige
    code_snippet: Optional[str] = None  # Contexto de código
    raw_output: dict = field(default_factory=dict)
