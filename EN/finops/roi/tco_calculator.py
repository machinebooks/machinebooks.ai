# Source: The FinOps Engineer and the Machine -- Chapter 23
# Pattern: Full TCO calculator (people + infra + AI)

# services/tco_calculator.py
# Service that calculates the real TCO of a project over a given period.
# Crosses people costs + LLM tokens + cloud + tools.

from datetime import date
from decimal import Decimal
from dataclasses import dataclass, field
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.imputacion import Imputacion
from models.perfil_coste import PerfilCoste


@dataclass
class DesgloseTCO:
    """Complete TCO breakdown of a project over a period."""
    proyecto_codigo: str
    mes_inicio: date
    mes_fin: date

    # People costs (sum of all allocations)
    coste_personas_eur: Decimal = Decimal("0.00")

    # LLM token costs (from LLMUsageLog, see Chapter 4)
    coste_tokens_eur: Decimal = Decimal("0.00")

    # Cloud infrastructure costs (from CloudCostAgent, see Chapter 12)
    coste_cloud_eur: Decimal = Decimal("0.00")

    # SaaS tools and licenses
    coste_herramientas_eur: Decimal = Decimal("0.00")

    # Breakdown by role profile (for analysis)
    desglose_por_perfil: dict = field(default_factory=dict)

    @property
    def coste_total(self) -> Decimal:
        return (self.coste_personas_eur + self.coste_tokens_eur +
                self.coste_cloud_eur + self.coste_herramientas_eur)

    @property
    def porcentaje_personas(self) -> float:
        if self.coste_total == 0:
            return 0.0
        return float(self.coste_personas_eur / self.coste_total * 100)

    @property
    def ratio_personas_vs_ia(self) -> float:
        """How many times more the team costs than the AI."""
        if self.coste_tokens_eur == 0:
            return float("inf")
        return float(self.coste_personas_eur / self.coste_tokens_eur)


class TCOCalculator:
    """
    Calculates the real TCO of a project integrating all cost sources.
    """

    def __init__(self, db: Session):
        self.db = db

    def calcular_tco(
        self,
        proyecto_codigo: str,
        mes_inicio: date,
        mes_fin: date,
        coste_tokens_eur: Decimal = Decimal("0"),
        coste_cloud_eur: Decimal = Decimal("0"),
        coste_herramientas_eur: Decimal = Decimal("0"),
    ) -> DesgloseTCO:
        """
        Calculates the complete TCO of a project over a month range.

        Token and cloud costs are passed as parameters because
        they come from external systems (LLMUsageLog, CloudCostAgent).
        People cost is calculated internally from the allocations.
        """
        desglose = DesgloseTCO(
            proyecto_codigo=proyecto_codigo,
            mes_inicio=mes_inicio,
            mes_fin=mes_fin,
            coste_tokens_eur=coste_tokens_eur,
            coste_cloud_eur=coste_cloud_eur,
            coste_herramientas_eur=coste_herramientas_eur,
        )

        # Retrieve all allocations for the project in the period
        imputaciones = (
            self.db.query(Imputacion)
            .join(PerfilCoste)
            .filter(
                Imputacion.proyecto_codigo == proyecto_codigo,
                Imputacion.mes >= mes_inicio,
                Imputacion.mes <= mes_fin,
            )
            .all()
        )

        # Calculate total people cost and breakdown by profile
        for imp in imputaciones:
            coste_imp = imp.calcular_coste_mes()
            desglose.coste_personas_eur += coste_imp

            perfil_nombre = imp.perfil_coste.nombre
            if perfil_nombre not in desglose.desglose_por_perfil:
                desglose.desglose_por_perfil[perfil_nombre] = Decimal("0")
            desglose.desglose_por_perfil[perfil_nombre] += coste_imp

        return desglose
