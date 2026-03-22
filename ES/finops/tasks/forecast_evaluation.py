# Extraído de: LibroFinOps/cap-16-forecasting.md
# tasks/forecast_evaluation.py

@celery_app.task(name='evaluate_forecast_accuracy')
def evaluate_forecast_accuracy(forecast_month: str):
    """
    Al cierre de cada mes, calcula el error del forecast.
    Se ejecuta el día 3 del mes siguiente, cuando la factura
    está finalizada.
    """
    db = next(get_db())

    forecasts = db.query(CostForecast).filter(
        CostForecast.forecast_month == forecast_month,
    ).order_by(CostForecast.generated_at).all()

    if not forecasts:
        return

    # Coste real del mes cerrado
    year, month = map(int, forecast_month.split('-'))
    actual_cost = _get_actual_monthly_cost(year, month)

    # Calculamos el error para cada forecast del mes
    for forecast in forecasts:
        if actual_cost > 0:
            forecast.actual_cost_usd = actual_cost
            forecast.forecast_error_pct = (
                (forecast.adjusted_forecast_usd - actual_cost)
                / actual_cost * 100
            )

    db.commit()
    db.close()
