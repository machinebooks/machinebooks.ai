# Extraído de: LibroDevSecOps/cap-25-madurez-devsecops.md
# maturity_model.py — Modelo de madurez DevSecOps en 6 dominios x 5 niveles
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

class Level(IntEnum):
    INEXISTENT = 0
    REACTIVE = 1
    REPEATABLE = 2
    DEFINED = 3
    OPTIMIZED = 4

@dataclass
class Criterion:
    id: str                    # Ej: "PS-2.3" (Pipeline Security, nivel 2, criterio 3)
    domain: str                # Código del dominio
    level: Level               # Nivel al que pertenece
    description: str           # Pregunta binaria
    verification: str          # Cómo se verifica (evidencia esperada)
    automated: bool = False    # ¿Se puede verificar automáticamente?

@dataclass
class DomainAssessment:
    domain: str
    achieved_level: Level
    criteria_met: dict[str, bool] = field(default_factory=dict)
    evidence: dict[str, str] = field(default_factory=dict)

MATURITY_MODEL: dict[str, dict[int, list[Criterion]]] = {
    "PS": {  # Pipeline Security
        1: [
            Criterion("PS-1.1", "PS", Level.REACTIVE,
                "¿Se ejecuta al menos un tipo de escaneo de seguridad (SAST, SCA o secrets)?",
                "Logs de CI con ejecución de Semgrep, Grype o Gitleaks"),
            Criterion("PS-1.2", "PS", Level.REACTIVE,
                "¿Los resultados del escaneo son visibles para el equipo de desarrollo?",
                "Captura de hallazgos accesibles en CI o dashboard"),
        ],
        2: [
            Criterion("PS-2.1", "PS", Level.REPEATABLE,
                "¿El escaneo SAST se ejecuta en cada PR automáticamente?",
                "Workflow de GitHub Actions con trigger on pull_request",
                automated=True),
            Criterion("PS-2.2", "PS", Level.REPEATABLE,
                "¿Existe al menos un gate que bloquee el merge por hallazgos CRITICAL?",
                "Configuración de branch protection + gate en workflow"),
            Criterion("PS-2.3", "PS", Level.REPEATABLE,
                "¿El escaneo SCA y de contenedores se ejecuta en cada build?",
                "Jobs de Grype y Trivy en pipeline CI"),
        ],
        3: [
            Criterion("PS-3.1", "PS", Level.DEFINED,
                "¿Las reglas de escaneo incluyen reglas custom además de las por defecto?",
                "Directorio de reglas Semgrep custom en el repositorio"),
            Criterion("PS-3.2", "PS", Level.DEFINED,
                "¿El DAST se ejecuta contra entornos de staging de forma periódica?",
                "Programación de escaneos DAST con ZAP o equivalente"),
        ],
        4: [
            Criterion("PS-4.1", "PS", Level.OPTIMIZED,
                "¿Las reglas de escaneo se generan o ajustan automáticamente con base en hallazgos históricos?",
                "Logs del agente de generación de reglas con métricas de precisión"),
            Criterion("PS-4.2", "PS", Level.OPTIMIZED,
                "¿La cobertura de escaneo supera el 95% de repos activos durante 6+ meses?",
                "Dashboard de cobertura con serie temporal",
                automated=True),
        ],
    },
    "AIS": {  # AI Security
        1: [
            Criterion("AIS-1.1", "AIS", Level.REACTIVE,
                "¿Existe un inventario de modelos LLM desplegados en producción?",
                "Documento o registro con modelos, versiones y endpoints"),
            Criterion("AIS-1.2", "AIS", Level.REACTIVE,
                "¿Se validan los inputs de usuario antes de enviarlos al LLM?",
                "Código de validación en el servicio de IA"),
        ],
        2: [
            Criterion("AIS-2.1", "AIS", Level.REPEATABLE,
                "¿Se ejecutan tests de prompt injection contra los endpoints LLM?",
                "Suite de tests adversariales con resultados documentados"),
            Criterion("AIS-2.2", "AIS", Level.REPEATABLE,
                "¿Los modelos desplegados tienen ML-BOM o model card documentada?",
                "Ficheros ML-BOM o model cards en el repositorio"),
        ],
        3: [
            Criterion("AIS-3.1", "AIS", Level.DEFINED,
                "¿Existe un agente de seguridad que audite periódicamente los endpoints LLM?",
                "Logs del agente de auditoría con calendario de ejecución"),
            Criterion("AIS-3.2", "AIS", Level.DEFINED,
                "¿Los agentes autónomos operan con principio de mínimo privilegio documentado?",
                "Configuración de permisos por agente con justificación"),
            Criterion("AIS-3.3", "AIS", Level.DEFINED,
                "¿El corpus RAG tiene validación de fuentes antes de indexar?",
                "Pipeline de ingestión con verificación de procedencia"),
        ],
        4: [
            Criterion("AIS-4.1", "AIS", Level.OPTIMIZED,
                "¿Las defensas contra prompt injection se ajustan con base en ataques detectados?",
                "Registro de actualizaciones de defensas con trigger de incidentes"),
            Criterion("AIS-4.2", "AIS", Level.OPTIMIZED,
                "¿La seguridad de modelos está integrada en el pipeline CI/CD con gates automáticos?",
                "Workflow con validación de modelo pre-deploy"),
        ],
    },
    # VM, GOV, MR y CA siguen la misma estructura — se omiten por brevedad
}
