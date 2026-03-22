# Source: The FinOps Engineer and the Machine -- Chapter 23
# Pattern: Team cost profile model (PerfilCoste)

# models/perfil_coste.py
# PerfilCoste model: real hourly cost by role type.
# Includes all components: salary, employer SS, structural overhead.

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PerfilCoste(Base):
    """
    Defines the real hourly cost of a role type.
    The coste_hora already includes social security, overhead, and
    benefit amortization. It is the total cost to the company, not the gross salary.
    """
    __tablename__ = "perfil_coste"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)  # e.g.: "ING_IA_SENIOR"
    nombre = Column(String(200), nullable=False)              # readable name

    # Base hourly cost in euros (real cost to the company)
    coste_hora_eur = Column(Numeric(10, 2), nullable=False)

    # Structural overhead factor (managers, HR, office, tools)
    # Typically 0.10 to 0.20 (10-20% additional on direct cost)
    factor_overhead = Column(Float, default=0.15)

    # Estimated productive hours per year for this profile
    # 1,660 hours/year * real efficiency (0.75-0.85)
    horas_productivas_anio = Column(Float, default=1.328)  # 1,660 * 0.80

    # Metadata
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def coste_hora_total(self) -> Decimal:
        """Hourly cost including structural overhead."""
        return self.coste_hora_eur * Decimal(str(1 + self.factor_overhead))

    @property
    def coste_mes_base(self) -> Decimal:
        """Estimated monthly cost at full dedication."""
        horas_mes = self.horas_productivas_anio / 12
        return self.coste_hora_total * Decimal(str(horas_mes))
