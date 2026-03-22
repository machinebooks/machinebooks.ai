# Extraído de: LibroTecnico/cap-22-observabilidad.md
# Endpoint de auditoría de consumo LLM para el panel Admin
# patrones/observabilidad/llm_audit_endpoint.py

from datetime import datetime, timezone
from sqlalchemy import func
from flask import Blueprint, request, jsonify
from models.llm_usage_log import LLMUsageLog
from auth.decorators import admin_required

admin_llm_bp = Blueprint('admin_llm', __name__)

@admin_llm_bp.route('/api/admin/llm-usage/summary', methods=['GET'])
@admin_required
def get_llm_usage_summary():
    """Resumen de consumo LLM agrupado por proveedor y modelo.

    Parámetros: ?days=30 (período de consulta, por defecto 30 días)
    Devuelve: coste total, tokens totales, latencia media y desglose por modelo.
    """
    days = request.args.get('days', 30, type=int)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Consulta agregada: coste, tokens y latencia por proveedor/modelo
    summary = db.session.query(
        LLMUsageLog.provider,
        LLMUsageLog.model,
        func.count(LLMUsageLog.id).label('total_calls'),
        func.sum(LLMUsageLog.total_cost_usd).label('total_cost'),
        func.sum(LLMUsageLog.input_tokens).label('total_input_tokens'),
        func.sum(LLMUsageLog.output_tokens).label('total_output_tokens'),
        func.avg(LLMUsageLog.latency_ms).label('avg_latency_ms'),
        # Tasa de error por modelo — útil para detectar degradación
        func.sum(
            func.if_(LLMUsageLog.status != 'success', 1, 0)
        ).label('error_count')
    ).filter(
        LLMUsageLog.created_at >= since
    ).group_by(
        LLMUsageLog.provider, LLMUsageLog.model
    ).all()

    return jsonify({
        "period_days": days,
        "models": [
            {
                "provider": row.provider,
                "model": row.model,
                "total_calls": row.total_calls,
                "total_cost_usd": round(row.total_cost or 0, 4),
                "total_input_tokens": row.total_input_tokens or 0,
                "total_output_tokens": row.total_output_tokens or 0,
                "avg_latency_ms": round(row.avg_latency_ms or 0, 1),
                "error_rate": round(
                    (row.error_count / row.total_calls) * 100, 2
                ) if row.total_calls > 0 else 0
            }
            for row in summary
        ]
    })
