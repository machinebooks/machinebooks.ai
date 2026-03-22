# Source: The FinOps Engineer and the Machine -- Chapter 23
# Pattern: Cost imputation model

# models/imputacion.py
# Monthly allocation record of people to projects.
# Granularity is monthly and based on dedication percentage.

from datetime import date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .perfil_coste import Base


class Imputacion(Base):
    """
    Records a person's dedication to a project in a specific month.
    Does not store personal identifiers: uses the cost profile and
    an anonymous person identifier within the team.
    """
    __tablename__ = "imputacion"

    id = Column(Integer, primary_key=True, index=True)

    # Reference to the cost profile (what role type this person is)
    perfil_coste_id = Column(Integer, ForeignKey("perfil_coste.id"), nullable=False)

    # Anonymous person identifier (not a name or email)
    # Can be "ENG-001", "PM-002", etc.
    persona_codigo = Column(String(50), nullable=False)

    # The project being allocated to (e.g.: "AI_PLATFORM", "CLIENT_PROJECT_X")
    proyecto_codigo = Column(String(100), nullable=False)

    # Month the allocation corresponds to (always the first day of the month)
    mes = Column(Date, nullable=False)

    # Dedication percentage: 0.0 to 1.0 (0% to 100%)
    # A person can have multiple allocations in the same month
    # if they work on multiple projects, with total sum <= 1.0
    porcentaje_dedicacion = Column(Numeric(5, 4), nullable=False)

    # Constraint: dedication between 0% and 100%
    __table_args__ = (
        CheckConstraint(
            "porcentaje_dedicacion >= 0.0 AND porcentaje_dedicacion <= 1.0",
            name="ck_dedicacion_rango"
        ),
    )

    # Relationship with the cost profile
    perfil_coste = relationship("PerfilCoste")

    def calcular_coste_mes(self) -> Decimal:
        """
        Calculates the monthly cost of this allocation.

        cost = total_hourly_cost * productive_hours_month * dedication_percentage
        """
        horas_productivas_mes = Decimal(
            str(self.perfil_coste.horas_productivas_anio / 12)
        )
        coste_hora = self.perfil_coste.coste_hora_total

        return coste_hora * horas_productivas_mes * self.porcentaje_dedicacion
