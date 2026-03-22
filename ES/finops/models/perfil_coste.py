# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# models/perfil_coste.py
# Modelo PerfilCoste: coste horario real por tipo de rol.
# Incluye todos los conceptos: salario, SS empresa, overhead estructural.

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PerfilCoste(Base):
    """
    Define el coste horario real de un tipo de rol.
    El coste_hora ya incluye seguridad social, overhead y amortización
    de beneficios. Es el coste total para la empresa, no el salario bruto.
    """
    __tablename__ = "perfil_coste"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)  # ej: "ING_IA_SENIOR"
    nombre = Column(String(200), nullable=False)              # nombre legible

    # Coste horario base en euros (coste real para la empresa)
    coste_hora_eur = Column(Numeric(10, 2), nullable=False)

    # Factor de overhead estructural (managers, RRHH, oficina, herramientas)
    # Típicamente 0.10 a 0.20 (10-20% adicional sobre el coste directo)
    factor_overhead = Column(Float, default=0.15)

    # Horas productivas anuales estimadas para este perfil
    # 1.660 horas/año × eficiencia real (0.75-0.85)
    horas_productivas_anio = Column(Float, default=1.328)  # 1.660 × 0.80

    # Metadatos
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def coste_hora_total(self) -> Decimal:
        """Coste horario incluyendo overhead estructural."""
        return self.coste_hora_eur * Decimal(str(1 + self.factor_overhead))

    @property
    def coste_mes_base(self) -> Decimal:
        """Coste mensual estimado a dedicación completa."""
        horas_mes = self.horas_productivas_anio / 12
        return self.coste_hora_total * Decimal(str(horas_mes))
