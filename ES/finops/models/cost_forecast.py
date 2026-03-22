# Extraído de: LibroFinOps/cap-16-forecasting.md
# models/cost_forecast.py
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from datetime import datetime
from database import Base


class CostForecast(Base):
    """
    Almacena los forecasts generados para trazabilidad y evaluación.
    La precisión real se calcula al cierre del mes comparando
    con la factura final.
    """
    __tablename__ = "cost_forecasts"

    id = Column(Integer, primary_key=True)
    provider = Column(String(20), nullable=False)   # 'aws', 'azure', 'all'
    forecast_month = Column(String(7), nullable=False)  # 'YYYY-MM'
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Componentes del forecast
    statistical_forecast_usd = Column(Float, nullable=False)
    adjusted_forecast_usd = Column(Float, nullable=False)
    forecast_range_low_usd = Column(Float, nullable=True)
    forecast_range_high_usd = Column(Float, nullable=True)

    # Contexto usado para el ajuste
    business_context_used = Column(String(2000), nullable=True)
    llm_explanation = Column(String(3000), nullable=True)

    # Evaluación posterior (se rellena al cerrar el mes)
    actual_cost_usd = Column(Float, nullable=True)
    forecast_error_pct = Column(Float, nullable=True)
