# Extraído de: LibroPQC/cap-16-dora.md
"""
Framework DORA para evaluación de preparación PQC.
Mapea artículos del Reglamento (UE) 2022/2554 a controles
de criptografía post-cuántica verificables.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class DoraCategory(Enum):
    """Categorías de obligación DORA con implicación PQC."""
    RISK_MANAGEMENT = "art_6_risk_management"
    PROTECTION = "art_9_protection_prevention"
    DETECTION = "art_10_detection"
    CONTINUITY = "art_11_continuity"
    TESTING = "art_26_resilience_testing"
    THIRD_PARTY = "art_28_third_party_risk"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"

@dataclass
class DoraControl:
    """Control DORA específico para preparación PQC."""
    control_id: str           # Ej: "DORA-PQC-6.1"
    article: int              # Artículo del reglamento
    category: DoraCategory
    description: str           # Requisito en lenguaje auditable
    verification_method: str   # Cómo se verifica el cumplimiento
    pqc_relevance: str         # Por qué afecta a la migración PQC
    weight: float = 1.0        # Peso en el scoring (configurable)

@dataclass
class DoraAssessment:
    """Evaluación DORA-PQC de una entidad financiera."""
    organization_id: int
    assessment_date: str
    controls: list = field(default_factory=list)
    findings_mapped: int = 0
    overall_score: float = 0.0
    status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED

    @property
    def critical_gaps(self) -> list:
        """Controles no conformes con peso alto."""
        return [c for c in self.controls
                if c.get("status") == "non_compliant"
                and c.get("weight", 1.0) >= 2.0]


# Catálogo de controles DORA-PQC
DORA_PQC_CONTROLS = [
    DoraControl(
        control_id="DORA-PQC-6.1",
        article=6,
        category=DoraCategory.RISK_MANAGEMENT,
        description=(
            "El marco de gestión de riesgos TIC incluye "
            "la amenaza cuántica como riesgo identificado"
        ),
        verification_method="inventory_exists",
        pqc_relevance=(
            "Art. 6 exige identificar TODAS las fuentes de riesgo TIC. "
            "La amenaza cuántica a la criptografía asimétrica es una "
            "fuente documentada por NIST, ENISA y Europol"
        ),
        weight=3.0,
    ),
    DoraControl(
        control_id="DORA-PQC-6.2",
        article=6,
        category=DoraCategory.RISK_MANAGEMENT,
        description=(
            "Existe un inventario criptográfico que identifica "
            "todos los usos de algoritmos quantum-vulnerables"
        ),
        verification_method="crypto_inventory_complete",
        pqc_relevance=(
            "Sin inventario criptográfico no es posible evaluar "
            "la exposición al riesgo cuántico ni planificar la migración"
        ),
        weight=3.0,
    ),
    DoraControl(
        control_id="DORA-PQC-9.1",
        article=9,
        category=DoraCategory.PROTECTION,
        description=(
            "Los mecanismos de cifrado en tránsito usan "
            "algoritmos resistentes o esquemas híbridos PQC"
        ),
        verification_method="tls_pqc_check",
        pqc_relevance=(
            "Art. 9 exige protección y prevención proporcional al riesgo. "
            "TLS con RSA/ECDH no proporciona protección contra HNDL"
        ),
        weight=2.5,
    ),
    DoraControl(
        control_id="DORA-PQC-9.2",
        article=9,
        category=DoraCategory.PROTECTION,
        description=(
            "Las firmas digitales de transacciones financieras "
            "usan algoritmos PQC o esquemas híbridos"
        ),
        verification_method="signature_pqc_check",
        pqc_relevance=(
            "Las firmas digitales garantizan integridad y no repudio "
            "de las transacciones. Un CRQC podría forjar firmas ECDSA/RSA"
        ),
        weight=3.0,
    ),
    DoraControl(
        control_id="DORA-PQC-11.1",
        article=11,
        category=DoraCategory.CONTINUITY,
        description=(
            "Los planes de continuidad contemplan el escenario "
            "de compromiso criptográfico por capacidad cuántica"
        ),
        verification_method="bcp_quantum_scenario",
        pqc_relevance=(
            "Art. 11 exige planes para perturbaciones graves de TIC. "
            "El compromiso de la criptografía asimétrica es una "
            "perturbación sistémica del sector financiero"
        ),
        weight=2.0,
    ),
    DoraControl(
        control_id="DORA-PQC-26.1",
        article=26,
        category=DoraCategory.TESTING,
        description=(
            "Las pruebas de resiliencia incluyen escenarios "
            "de ataque con capacidad criptográfica cuántica"
        ),
        verification_method="tlpt_quantum_scenarios",
        pqc_relevance=(
            "Art. 26 exige pruebas basadas en amenazas actualizadas. "
            "La amenaza cuántica a la criptografía está documentada "
            "como amenaza activa (HNDL) por Europol y ENISA"
        ),
        weight=2.0,
    ),
    DoraControl(
        control_id="DORA-PQC-28.1",
        article=28,
        category=DoraCategory.THIRD_PARTY,
        description=(
            "Los acuerdos con proveedores TIC críticos incluyen "
            "cláusulas de preparación criptográfica post-cuántica"
        ),
        verification_method="third_party_pqc_clauses",
        pqc_relevance=(
            "Art. 28 exige gestión del riesgo de terceros TIC. "
            "Un proveedor que no migre a PQC expone a la entidad "
            "financiera a riesgo criptográfico indirecto"
        ),
        weight=2.0,
    ),
]
