# Extraído de: LibroFinOps/cap-11-presupuestos-circuit-breakers.md
# models/budget_config.py
from sqlalchemy import Column, String, Float, Integer, Enum, DateTime, Boolean
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class BudgetScope(str, enum.Enum):
    """Alcance de un presupuesto: global, por servicio o por usuario."""
    GLOBAL  = "global"
    SERVICE = "service"
    USER    = "user"

class BudgetPeriod(str, enum.Enum):
    """Periodo de renovación del presupuesto."""
    DAILY   = "daily"
    WEEKLY  = "weekly"
    MONTHLY = "monthly"

class BudgetConfig(Base):
    """Configuración de presupuestos con los tres niveles de respuesta."""
    __tablename__ = "budget_config"

    id             = Column(Integer, primary_key=True)
    name           = Column(String(100), unique=True)  # identificador legible
    scope          = Column(Enum(BudgetScope))
    scope_id       = Column(String(100), nullable=True)  # servicio o user_id
    period         = Column(Enum(BudgetPeriod), default=BudgetPeriod.MONTHLY)
    # Límite máximo en USD para el periodo
    limit_usd      = Column(Float)
    # Umbrales de activación de cada nivel (fracción del límite)
    alert_threshold    = Column(Float, default=0.80)  # 80%
    throttle_threshold = Column(Float, default=0.95)  # 95%
    block_threshold    = Column(Float, default=1.00)  # 100%
    # Estado actual (actualizado por el enforcement middleware)
    current_spend_usd  = Column(Float, default=0.0)
    period_start       = Column(DateTime)
    is_active          = Column(Boolean, default=True)
    updated_at         = Column(DateTime)
