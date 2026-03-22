# Extraído de: LibroCISO/cap-10-arquitectura-llm.md
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from app.models.base import BaseModel
from app.models.ai import AIProvider

import logging

logger = logging.getLogger(__name__)


class AIUsageRecord(BaseModel):
    """Registro de uso individual de IA para tracking financiero."""
    __tablename__ = "ai_usage_records"

    service_name = Column(String(100), nullable=False, index=True)
    provider_name = Column(String(100), nullable=False, index=True)
    model_name = Column(String(200), nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    estimated_cost_eur = Column(Float, nullable=False)
    user_id = Column(String(200), nullable=True)
    tenant_id = Column(Integer, nullable=True)  # Para reportes multi-tenant
    fallback_used = Column(Boolean, default=False)
    fallback_level = Column(Integer, nullable=True)


def record_usage(
    db,
    service_name: str,
    provider_name: str,
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    user_id: str = None,
    tenant_id: int = None,
    fallback_used: bool = False,
    fallback_level: int = None
):
    """Registra el uso y calcula el coste estimado."""
    # Obtener precios del proveedor
    provider = db.query(AIProvider).filter(
        AIProvider.name == provider_name
    ).first()

    cost = 0.0
    if provider and provider.available_models:
        for model_info in provider.available_models:
            if model_info["name"] == model_name:
                # Precios por millón de tokens → coste de esta llamada
                input_cost = (input_tokens / 1_000_000) * model_info.get("input_price", 0)
                output_cost = (output_tokens / 1_000_000) * model_info.get("output_price", 0)
                cost = round(input_cost + output_cost, 6)
                break

    # Crear registro
    record = AIUsageRecord(
        service_name=service_name,
        provider_name=provider_name,
        model_name=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        estimated_cost_eur=cost,
        user_id=user_id,
        tenant_id=tenant_id,
        fallback_used=fallback_used,
        fallback_level=fallback_level
    )
    db.add(record)

    # Actualizar gasto acumulado del proveedor
    if provider:
        provider.monthly_spent = (provider.monthly_spent or 0) + cost

        # Alertas de presupuesto
        if provider.monthly_budget and provider.monthly_budget > 0:
            usage_pct = (provider.monthly_spent / provider.monthly_budget) * 100
            if usage_pct >= 100:
                logger.warning(
                    f"PRESUPUESTO AGOTADO: {provider.display_name} "
                    f"({provider.monthly_spent:.2f}€ / {provider.monthly_budget:.2f}€)"
                )
            elif usage_pct >= 80:
                logger.warning(
                    f"Presupuesto al {usage_pct:.0f}%: {provider.display_name} "
                    f"({provider.monthly_spent:.2f}€ / {provider.monthly_budget:.2f}€)"
                )

    db.commit()
    return record
