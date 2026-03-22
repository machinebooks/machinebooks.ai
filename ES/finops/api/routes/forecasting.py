# Extraído de: LibroFinOps/cap-16-forecasting.md
# api/routes/forecasting.py
from fastapi import APIRouter, HTTPException
from datetime import date

router = APIRouter(prefix="/forecasting", tags=["Forecasting"])


@router.get("/current-month")
async def get_current_month_forecast():
    """
    Devuelve el forecast del mes actual con explicación.
    Diseñado para el dashboard del CFO.
    """
    db = next(get_db())
    today = date.today()
    forecast_month = today.strftime('%Y-%m')

    latest = db.query(CostForecast).filter(
        CostForecast.forecast_month == forecast_month,
        CostForecast.provider == 'all'
    ).order_by(CostForecast.generated_at.desc()).first()

    if not latest:
        raise HTTPException(
            status_code=404, detail="Forecast no disponible"
        )

    budget = get_monthly_budget()
    deviation_pct = (
        (latest.adjusted_forecast_usd - budget) / budget * 100
        if budget > 0 else 0
    )

    return {
        'forecast_month': forecast_month,
        'generated_at': latest.generated_at.isoformat(),
        'forecast': {
            'expected_usd': latest.adjusted_forecast_usd,
            'range_low_usd': latest.forecast_range_low_usd,
            'range_high_usd': latest.forecast_range_high_usd,
            'statistical_base_usd': latest.statistical_forecast_usd
        },
        'vs_budget': {
            'budget_usd': budget,
            'deviation_pct': round(deviation_pct, 1),
            'status': (
                'over_budget' if deviation_pct > 5 else 'on_track'
            )
        },
        'explanation': latest.llm_explanation,
        'data_as_of': f"Día {today.day} de {today.strftime('%B')}"
    }
