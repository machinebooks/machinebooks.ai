# Source: The DevSecOps and the Machine -- Chapter 25
# Pattern: DevSecOps maturity model with automated assessment

# maturity_model.py
from dataclasses import dataclass, field
from enum import IntEnum

class Level(IntEnum):
    INEXISTENT = 0
    REACTIVE = 1
    REPEATABLE = 2
    DEFINED = 3
    OPTIMIZED = 4

@dataclass
class Criterion:
    id: str
    domain: str
    level: Level
    description: str
    verification: str
    automated: bool = False

MATURITY_MODEL: dict[str, dict[int, list[Criterion]]] = {
    "PS": {
        1: [
            Criterion("PS-1.1", "PS", Level.REACTIVE,
                "¿Se ejecuta al menos un tipo de escaneo de seguridad (SAST, SCA o secrets)?",
                "Logs de CI con ejecución de Semgrep, Grype o Gitleaks"),
        ],
        2: [
            Criterion("PS-2.1", "PS", Level.REPEATABLE,
                "¿El escaneo SAST se ejecuta en cada PR automáticamente?",
                "Workflow de GitHub Actions con trigger on pull_request",
                automated=True),
            Criterion("PS-2.2", "PS", Level.REPEATABLE,
                "¿Existe al menos un gate que bloquee el merge por hallazgos CRITICAL?",
                "Configuración de branch protection + gate en workflow"),
        ],
        3: [
            Criterion("PS-3.1", "PS", Level.DEFINED,
                "¿Las reglas de escaneo incluyen reglas custom además de las por defecto?",
                "Directorio de reglas Semgrep custom en el repositorio"),
        ],
        4: [
            Criterion("PS-4.1", "PS", Level.OPTIMIZED,
                "¿Las reglas de escaneo se generan o ajustan automáticamente con base en hallazgos históricos?",
                "Logs del agente de generación de reglas con métricas de precisión"),
        ],
    },
    "AIS": {
        1: [
            Criterion("AIS-1.1", "AIS", Level.REACTIVE,
                "¿Existe un inventario de modelos LLM desplegados en producción?",
                "Documento o registro con modelos, versiones y endpoints"),
        ],
        2: [
            Criterion("AIS-2.1", "AIS", Level.REPEATABLE,
                "¿Se ejecutan tests de prompt injection contra los endpoints LLM?",
                "Suite de tests adversariales con resultados documentados"),
        ],
    },
}