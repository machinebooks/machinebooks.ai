# Extraído de: LibroFinOps/cap-16-forecasting.md
# forecasting/statistical_engine.py
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from models.cloud_cost_metric import CloudCostMetric
from sqlalchemy.orm import Session


class StatisticalForecaster:
    """
    Motor de forecasting basado en media móvil exponencial
    con ajuste estacional. Determinista y auditable.
    """

    def __init__(self, db: Session, provider: str = 'all'):
        self.db = db
        self.provider = provider

    def forecast_current_month(self) -> dict:
        """
        Proyecta el gasto del mes actual usando:
        1. Ritmo de gasto de los días transcurridos
        2. Tendencia de los últimos 90 días (EWMA)
        3. Factor de estacionalidad del mes actual
        """
        today = date.today()
        days_elapsed = today.day
        days_in_month = (
            date(today.year, today.month + 1, 1)
            - date(today.year, today.month, 1)
        ).days
        days_remaining = days_in_month - days_elapsed

        # Gasto acumulado en lo que va de mes
        month_start = datetime(today.year, today.month, 1)
        current_cost = self._get_total_cost(
            month_start, datetime.utcnow()
        )

        # Proyección simple: ritmo diario actual * días restantes
        daily_rate = current_cost / days_elapsed if days_elapsed > 0 else 0
        simple_projection = current_cost + (daily_rate * days_remaining)

        # Tendencia EWMA de los últimos 6 meses
        trend = self._calculate_ewma_trend()

        # Factor de estacionalidad del año anterior
        seasonality = self._calculate_seasonality(today.month)

        # Proyección ajustada con tendencia y estacionalidad
        adjusted = simple_projection * seasonality * (1 + trend)

        return {
            'simple_projection_usd': round(simple_projection, 2),
            'trend_adjusted_projection_usd': round(adjusted, 2),
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'current_month_spend_usd': round(current_cost, 2),
            'daily_rate_usd': round(daily_rate, 2),
            'seasonality_factor': round(seasonality, 3),
            'trend_factor': round(trend, 3)
        }
