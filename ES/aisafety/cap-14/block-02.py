# Extraido de: LibroAISafety/cap-14-infraestructura.md
# Checklist automatizable de evaluación de infraestructura de IA
# Código didáctico — los tests reales requieren herramientas específicas

from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Finding:
    component: str
    check: str
    severity: Severity
    description: str
    recommendation: str

def evaluar_electron(app_path: str) -> list[Finding]:
    """Evaluación de seguridad para aplicación Electron."""
    findings = []

    # Check 1: Integridad del ASAR
    # ¿Se puede extraer, modificar y reempaquetar sin detección?
    findings.append(Finding(
        component="electron",
        check="asar_integrity",
        severity=Severity.HIGH,
        description="El ASAR no tiene verificación de integridad. "
                    "Un atacante local puede modificar el código de la aplicación.",
        recommendation="Implementar asar-integrity o verificación de hash al arranque."
    ))

    # Check 2: Firma de binarios
    # ¿Los ejecutables y DLLs están firmados?
    findings.append(Finding(
        component="electron",
        check="binary_signing",
        severity=Severity.MEDIUM,
        description="Binarios auxiliares no están firmados. "
                    "Susceptibles a sustitución.",
        recommendation="Firmar todos los binarios con certificado de code signing."
    ))

    # Check 3: DLL search path
    # ¿La aplicación carga DLLs de ubicaciones inseguras?
    findings.append(Finding(
        component="electron",
        check="dll_search_path",
        severity=Severity.HIGH,
        description="La aplicación busca DLLs en el directorio de trabajo "
                    "antes que en rutas del sistema.",
        recommendation="Usar SetDllDirectory o rutas absolutas para cargar DLLs."
    ))

    return findings
