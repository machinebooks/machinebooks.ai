# Source: The FinOps Engineer and the Machine -- Chapter 16
# Pattern: Forecast accuracy evaluation

# tasks/forecast_evaluation.py

@celery_app.task(name='evaluate_forecast_accuracy')
def evaluate_forecast_accuracy(forecast_month: str):
    """
    At each month's close, calculates forecast error.
    Runs on the 3rd of the following month, when the invoice
    is finalized.
    """
    db = next(get_db())

    forecasts = db.query(CostForecast).filter(
        CostForecast.forecast_month == forecast_month,
    ).order_by(CostForecast.generated_at).all()

    if not forecasts:
        return

    # Actual cost of the closed month
    year, month = map(int, forecast_month.split('-'))
    actual_cost = _get_actual_monthly_cost(year, month)

    # Calculate error for each month's forecast
    for forecast in forecasts:
        if actual_cost > 0:
            forecast.actual_cost_usd = actual_cost
            forecast.forecast_error_pct = (
                (forecast.adjusted_forecast_usd - actual_cost)
                / actual_cost * 100
            )

    db.commit()
    db.close()
