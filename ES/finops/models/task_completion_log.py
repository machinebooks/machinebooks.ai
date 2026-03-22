# Extraído de: LibroFinOps/cap-01-la-factura.md
# models/task_completion_log.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class TaskCompletionLog(Base):
    """Registro de tarea completada con IA.
    Compara duración real vs. línea base humana."""
    __tablename__ = "task_completion_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(
        String(50), nullable=False  # "offer_gen", "risk_analysis"
    )
    ai_duration_seconds = Column(Float, nullable=False)
    human_baseline_minutes = Column(Float, nullable=False)
    hourly_cost_eur = Column(
        Float, nullable=False, default=50.0
    )
    time_saved_minutes = Column(Float, nullable=False)
    money_saved_eur = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
