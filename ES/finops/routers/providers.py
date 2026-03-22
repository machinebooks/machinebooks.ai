# Extraído de: LibroFinOps/cap-22-multiproveedor.md
# routers/providers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.llm_pricing import LLMModelPricing
from auth import require_role

router = APIRouter(prefix="/api/v1/providers", tags=["Proveedores LLM"])


@router.get("/")
def list_providers(
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin", "finops"])),
):
    """Lista todos los proveedores con estado, coste, y coste efectivo."""
    models = db.query(LLMModelPricing).order_by(
        LLMModelPricing.active.desc(), LLMModelPricing.priority
    ).all()
    return [
        {
            "model_id": m.model_id,
            "provider": m.provider,
            "active": m.active,
            "health_status": m.health_status,
            "price_input_per_1m_usd": m.price_input_per_1m,
            "effective_input_price": (
                m.price_input_per_1m * (1 - (m.committed_use_discount or 0))
            ),
            "latency_p95_ms": m.latency_p95_ms,
            "quality_score_avg": m.quality_score_avg,
        }
        for m in models
    ]


@router.patch("/{model_id}/activate")
def activate_provider(
    model_id: str,
    priority: int = 10,
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin", "finops"])),
):
    """Activa un proveedor sin cambios de código."""
    model = db.query(LLMModelPricing).filter(
        LLMModelPricing.model_id == model_id
    ).first()
    if not model:
        raise HTTPException(404, "Proveedor no encontrado")
    model.active = True
    model.priority = priority
    db.commit()
    return {"message": f"{model_id} activado con prioridad {priority}"}
