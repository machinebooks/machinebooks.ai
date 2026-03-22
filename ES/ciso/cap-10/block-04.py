# Extraído de: LibroCISO/cap-10-arquitectura-llm.md
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import require_role
from app.extensions import get_db
from app.models.ai import AIProvider, AIServiceConfig, AIPrompt
from app.schemas.ai_admin import (
    AIProviderUpdate, AIServiceConfigUpdate, AIPromptCreate,
    AIProviderResponse, AIServiceConfigResponse, UsageSummaryResponse
)
from sqlalchemy import func
from datetime import datetime

router = APIRouter(prefix="/api/v1/admin/ai", tags=["AI Admin"])


@router.get("/providers", response_model=list[AIProviderResponse])
async def list_providers(
    db=Depends(get_db),
    _=Depends(require_role("admin"))
):
    """Lista todos los proveedores de LLM con su estado actual."""
    providers = db.query(AIProvider).filter(
        AIProvider.is_deleted == False
    ).all()
    return providers


@router.put("/providers/{provider_id}")
async def update_provider(
    provider_id: int,
    data: AIProviderUpdate,
    db=Depends(get_db),
    _=Depends(require_role("admin"))
):
    """
    Actualiza la configuración de un proveedor.
    Permite cambiar modelos, precios, presupuesto y estado activo/inactivo.
    """
    provider = db.query(AIProvider).get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(provider, field, value)

    db.commit()
    return {"status": "updated", "provider": provider.name}


@router.put("/services/{service_name}")
async def update_service_config(
    service_name: str,
    data: AIServiceConfigUpdate,
    db=Depends(get_db),
    _=Depends(require_role("admin"))
):
    """
    Actualiza la configuración de un servicio de IA.
    Cambiar modelo, temperatura, guardrails o fallback tiene efecto inmediato.
    """
    config = db.query(AIServiceConfig).filter(
        AIServiceConfig.service_name == service_name
    ).first()
    if not config:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(config, field, value)

    db.commit()
    return {"status": "updated", "service": service_name}


@router.post("/prompts")
async def create_prompt_version(
    data: AIPromptCreate,
    db=Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    """
    Crea una nueva versión del prompt para un servicio.
    Si activate=true, desactiva la versión anterior y activa la nueva.
    """
    # Obtener la última versión
    last = db.query(func.max(AIPrompt.version)).filter(
        AIPrompt.service_name == data.service_name
    ).scalar() or 0

    prompt = AIPrompt(
        service_name=data.service_name,
        version=last + 1,
        prompt_text=data.prompt_text,
        created_by=current_user.username,
        notes=data.notes,
        is_active=False
    )
    db.add(prompt)

    if data.activate:
        # Desactivar prompts anteriores del mismo servicio
        db.query(AIPrompt).filter(
            AIPrompt.service_name == data.service_name,
            AIPrompt.is_active == True
        ).update({"is_active": False})
        prompt.is_active = True

        # Actualizar referencia en el servicio
        config = db.query(AIServiceConfig).filter(
            AIServiceConfig.service_name == data.service_name
        ).first()
        if config:
            config.active_prompt_id = prompt.id

    db.commit()
    return {"status": "created", "version": prompt.version, "active": prompt.is_active}


@router.get("/usage/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    period: str = "month",  # "day", "week", "month"
    db=Depends(get_db),
    _=Depends(require_role("admin"))
):
    """
    Resumen de uso y coste de IA agrupado por proveedor y servicio.
    Alimenta el panel de control de gobernanza de IA.
    """
    from app.models.ai import AIUsageRecord

    # Coste total por proveedor
    provider_costs = db.query(
        AIUsageRecord.provider_name,
        func.sum(AIUsageRecord.estimated_cost_eur).label("total_cost"),
        func.sum(AIUsageRecord.input_tokens).label("total_input_tokens"),
        func.sum(AIUsageRecord.output_tokens).label("total_output_tokens"),
        func.avg(AIUsageRecord.latency_ms).label("avg_latency"),
        func.count(AIUsageRecord.id).label("total_calls")
    ).group_by(
        AIUsageRecord.provider_name
    ).all()

    # Coste total por servicio
    service_costs = db.query(
        AIUsageRecord.service_name,
        func.sum(AIUsageRecord.estimated_cost_eur).label("total_cost"),
        func.count(AIUsageRecord.id).label("total_calls"),
        func.avg(AIUsageRecord.latency_ms).label("avg_latency")
    ).group_by(
        AIUsageRecord.service_name
    ).all()

    return {
        "by_provider": [
            {
                "provider": r.provider_name,
                "total_cost": round(r.total_cost or 0, 2),
                "total_tokens": (r.total_input_tokens or 0) + (r.total_output_tokens or 0),
                "avg_latency_ms": round(r.avg_latency or 0),
                "total_calls": r.total_calls
            }
            for r in provider_costs
        ],
        "by_service": [
            {
                "service": r.service_name,
                "total_cost": round(r.total_cost or 0, 2),
                "total_calls": r.total_calls,
                "avg_latency_ms": round(r.avg_latency or 0)
            }
            for r in service_costs
        ]
    }
