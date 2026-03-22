# Source: The FinOps Engineer and the Machine -- Chapter 16
# Pattern: Celery forecasting pipeline

# tasks/forecasting.py
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, date
from forecasting.statistical_engine import StatisticalForecaster
from forecasting.llm_adjuster import adjust_forecast_with_context
from models.cost_forecast import CostForecast

celery_app = Celery('forecasting')


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily forecast at 8 AM
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        generate_monthly_forecast.s(),
        name='generate-monthly-forecast-daily'
    )


@celery_app.task(name='generate_monthly_forecast')
def generate_monthly_forecast():
    """
    Generates the current month's forecast combining statistics and LLM.
    Runs daily to incorporate real accumulated spend.
    """
    db = next(get_db())
    today = date.today()
    forecast_month = today.strftime('%Y-%m')

    # Statistical layer
    forecaster = StatisticalForecaster(db=db, provider='all')
    statistical_data = forecaster.forecast_current_month()

    # Business context for the period
    business_context = get_forecast_business_context(
        target_month=forecast_month
    )
    historical_context = _get_historical_context(
        month=today.month, years_back=2
    )

    # LLM adjustment
    adjusted = adjust_forecast_with_context(
        statistical_data=statistical_data,
        business_context=business_context,
        historical_context=historical_context
    )

    # Save with full traceability
    forecast_record = CostForecast(
        provider='all',
        forecast_month=forecast_month,
        statistical_forecast_usd=statistical_data[
            'trend_adjusted_projection_usd'
        ],
        adjusted_forecast_usd=adjusted['adjusted_forecast_usd'],
        forecast_range_low_usd=adjusted['range_low_usd'],
        forecast_range_high_usd=adjusted['range_high_usd'],
        business_context_used=business_context,
        llm_explanation=adjusted.get('executive_summary', '')
    )
    db.add(forecast_record)
    db.commit()
    db.close()

    return {
        'forecast_month': forecast_month,
        'adjusted_forecast_usd': adjusted['adjusted_forecast_usd'],
        'range': (
            f"${adjusted['range_low_usd']:.0f}"
            f" - ${adjusted['range_high_usd']:.0f}"
        )
    }
