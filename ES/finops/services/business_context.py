# Extraído de: LibroFinOps/cap-13-anomaly-detection.md
# services/business_context.py
from datetime import datetime, date


def get_current_business_context() -> str:
    """
    Construye el contexto de negocio actual para enriquecer el análisis.
    En producción: conectar con el sistema de CI/CD, CRM y calendarios.
    """
    context_parts = []
    today = date.today()

    # Despliegues recientes (integración con el sistema de CI/CD)
    recent_deployments = _get_recent_deployments()
    if recent_deployments:
        context_parts.append(
            f"Despliegues en las últimas 24h: {', '.join(recent_deployments)}"
        )

    # Eventos de negocio planificados
    planned_events = _get_planned_events(today)
    if planned_events:
        context_parts.append(
            f"Eventos planificados esta semana: {', '.join(planned_events)}"
        )

    # Estado del presupuesto mensual
    budget_status = _get_budget_status()
    context_parts.append(
        f"Presupuesto mensual: ${budget_status['total_budget']:.0f}, "
        f"consumido: {budget_status['pct_used']:.1f}% "
        f"(día {today.day} del mes)"
    )

    context_parts.append(
        f"Día actual: {today.strftime('%A')} {today.strftime('%d/%m/%Y')}"
    )

    return "\n".join(context_parts) if context_parts else "Sin contexto adicional"
