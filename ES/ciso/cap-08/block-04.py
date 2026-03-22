# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/seed.py

import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.compliance import (
    ComplianceFramework, ComplianceControl, FrameworkCategory
)

SEED_DIR = Path(__file__).parent / "seed_data"

def seed_framework(db: Session, filename: str) -> ComplianceFramework:
    """Carga un marco completo desde fichero JSON."""
    data = json.loads((SEED_DIR / filename).read_text(encoding="utf-8"))

    # Verificar si ya existe (idempotente)
    existing = db.query(ComplianceFramework).filter_by(
        code=data["code"]
    ).first()
    if existing:
        return existing

    framework = ComplianceFramework(
        code=data["code"],
        name=data["name"],
        version=data["version"],
        category=FrameworkCategory(data["category"]),
        description=data["description"],
        official_url=data.get("official_url"),
        total_controls=data.get("total_controls", 0)
    )
    db.add(framework)
    db.flush()  # Obtener ID antes de crear controles

    # Crear controles con jerarquía
    _create_controls_recursive(
        db, framework.id, data.get("controls", []), parent_id=None
    )
    db.commit()
    return framework


def _create_controls_recursive(
    db: Session,
    framework_id: int,
    controls: list[dict],
    parent_id: int | None
):
    """Crea controles recursivamente respetando jerarquía."""
    for ctrl_data in controls:
        control = ComplianceControl(
            framework_id=framework_id,
            parent_id=parent_id,
            code=ctrl_data["code"],
            name=ctrl_data["name"],
            description=ctrl_data.get("description"),
            guidance=ctrl_data.get("guidance"),
            level=ctrl_data.get("level", 0),
            level_requirements=ctrl_data.get("level_requirements")
        )
        db.add(control)
        db.flush()

        # Procesar hijos recursivamente
        if "children" in ctrl_data:
            _create_controls_recursive(
                db, framework_id, ctrl_data["children"], control.id
            )
