# Extraído de: LibroPQC/cap-24-saas.md
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.models.organization import Organization
from app.models.user import User
from app.models.analysis import AnalysisJob


def calculate_saas_metrics():
    """Calcula métricas SaaS operativas.

    Estas métricas se consultan en el panel interno de administración,
    no se exponen a los usuarios de la plataforma.
    """
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    # Distribución de organizaciones por plan
    plan_distribution = dict(
        db.session.query(
            Organization.subscription_plan,
            func.count(Organization.id)
        ).filter(
            Organization.is_active == True
        ).group_by(
            Organization.subscription_plan
        ).all()
    )

    # Organizaciones activas (al menos 1 análisis en 30 días)
    active_orgs = db.session.query(
        func.count(func.distinct(AnalysisJob.organization_id))
    ).filter(
        AnalysisJob.created_at >= thirty_days_ago
    ).scalar()

    # Análisis totales este mes
    monthly_analyses = AnalysisJob.query.filter(
        extract('year', AnalysisJob.created_at) == now.year,
        extract('month', AnalysisJob.created_at) == now.month
    ).count()

    # Tasa de uso: qué porcentaje de su cuota usan las orgs
    # (indicador de actividad y de presión para upgrade)
    usage_rates = []
    orgs = Organization.query.filter_by(is_active=True).all()
    for org in orgs:
        if org.subscription_plan == 'enterprise':
            continue  # Enterprise no tiene límite numérico
        month_usage = AnalysisJob.query.filter(
            AnalysisJob.organization_id == org.id,
            extract('year', AnalysisJob.created_at) == now.year,
            extract('month', AnalysisJob.created_at) == now.month
        ).count()
        if org.max_analyses_per_month > 0:
            rate = month_usage / org.max_analyses_per_month
            usage_rates.append({
                'org_id': org.id,
                'plan': org.subscription_plan,
                'usage_rate': round(rate, 2)
            })

    return {
        'plan_distribution': plan_distribution,
        'active_organizations_30d': active_orgs,
        'monthly_analyses': monthly_analyses,
        'usage_rates': usage_rates,
        'avg_usage_rate': (
            sum(r['usage_rate'] for r in usage_rates) / len(usage_rates)
            if usage_rates else 0
        )
    }
