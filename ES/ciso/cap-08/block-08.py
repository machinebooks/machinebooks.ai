# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/soa.py

from datetime import datetime
from sqlalchemy.orm import Session
import hashlib
import json

def generate_soa(
    db: Session,
    framework_id: int,
    format: str = "json"
) -> dict:
    """
    Genera la Declaración de Aplicabilidad (SoA) desde el estado
    actual de los controles. La SoA no es un documento estático:
    es una vista en tiempo real del estado de cumplimiento.
    """
    framework = db.query(ComplianceFramework).get(framework_id)
    controls = db.query(ComplianceControl).filter(
        ComplianceControl.framework_id == framework_id,
        ComplianceControl.level > 0  # Solo controles, no categorías
    ).order_by(ComplianceControl.code).all()

    soa_entries = []
    for control in controls:
        entry = {
            "code": control.code,
            "name": control.name,
            "applicable": (
                control.compliance_status
                != ComplianceStatus.NOT_APPLICABLE
            ),
            "justification": (
                control.not_applicable_justification
                if control.compliance_status
                    == ComplianceStatus.NOT_APPLICABLE
                else None
            ),
            "compliance_status": control.compliance_status.value,
            "implementation_status": control.implementation_status.value,
            "evidence_count": len([
                e for e in control.evidences if e.is_valid
            ]),
            "last_evidence": max(
                (e.collected_at.isoformat() for e in control.evidences),
                default=None
            )
        }
        soa_entries.append(entry)

    # Estadísticas agregadas
    applicable = [e for e in soa_entries if e["applicable"]]
    soa = {
        "framework": {
            "code": framework.code,
            "name": framework.name,
            "version": framework.version
        },
        "generated_at": datetime.utcnow().isoformat(),
        "statistics": {
            "total_controls": len(soa_entries),
            "applicable": len(applicable),
            "not_applicable": len(soa_entries) - len(applicable),
            "compliant": len([
                e for e in applicable
                if e["compliance_status"] == "compliant"
            ]),
            "partially_compliant": len([
                e for e in applicable
                if e["compliance_status"] == "partially_compliant"
            ]),
            "non_compliant": len([
                e for e in applicable
                if e["compliance_status"] == "non_compliant"
            ]),
            "not_assessed": len([
                e for e in applicable
                if e["compliance_status"] == "not_assessed"
            ])
        },
        "entries": soa_entries
    }

    # Hash de integridad para verificar que no se modifica post-exportación
    soa["integrity_hash"] = hashlib.sha256(
        json.dumps(soa["entries"], sort_keys=True).encode()
    ).hexdigest()

    return soa
