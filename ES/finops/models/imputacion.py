# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# models/imputacion.py
# Registro de dedicación mensual de personas a proyectos.
# La granularidad es mensual y se basa en porcentaje de dedicación.

from datetime import date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .perfil_coste import Base


class Imputacion(Base):
    """
    Registra la dedicación de una persona a un proyecto en un mes concreto.
    No almacena identificadores personales: usa el perfil de coste y
    un identificador anónimo de persona dentro del equipo.
    """
    __tablename__ = "imputacion"

    id = Column(Integer, primary_key=True, index=True)

    # Referencia al perfil de coste (qué tipo de rol es esta persona)
    perfil_coste_id = Column(Integer, ForeignKey("perfil_coste.id"), nullable=False)

    # Identificador anónimo de la persona (no es nombre ni email)
    # Puede ser "ENG-001", "PM-002", etc.
    persona_codigo = Column(String(50), nullable=False)

    # El proyecto al que se imputa (ej: "PLATAFORMA_IA", "PROYECTO_CLIENTE_X")
    proyecto_codigo = Column(String(100), nullable=False)

    # Mes al que corresponde la imputación (siempre primer día del mes)
    mes = Column(Date, nullable=False)

    # Porcentaje de dedicación: 0.0 a 1.0 (0% a 100%)
    # Una persona puede tener múltiples imputaciones en el mismo mes
    # si trabaja en varios proyectos, con suma total <= 1.0
    porcentaje_dedicacion = Column(Numeric(5, 4), nullable=False)

    # Restricción: dedicación entre 0% y 100%
    __table_args__ = (
        CheckConstraint(
            "porcentaje_dedicacion >= 0.0 AND porcentaje_dedicacion <= 1.0",
            name="ck_dedicacion_rango"
        ),
    )

    # Relación con el perfil de coste
    perfil_coste = relationship("PerfilCoste")

    def calcular_coste_mes(self) -> Decimal:
        """
        Calcula el coste mensual de esta imputación.

        coste = coste_hora_total × horas_productivas_mes × porcentaje_dedicacion
        """
        horas_productivas_mes = Decimal(
            str(self.perfil_coste.horas_productivas_anio / 12)
        )
        coste_hora = self.perfil_coste.coste_hora_total

        return coste_hora * horas_productivas_mes * self.porcentaje_dedicacion
