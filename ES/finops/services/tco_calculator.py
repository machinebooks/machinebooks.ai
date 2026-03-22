# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# services/tco_calculator.py
# Servicio que calcula el TCO real de un proyecto en un período dado.
# Cruza costes de personas + tokens LLM + cloud + herramientas.

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
    """Desglose completo del TCO de un proyecto en un período."""
    proyecto_codigo: str
    mes_inicio: date
    mes_fin: date

    # Costes de personas (suma de todas las imputaciones)
    coste_personas_eur: Decimal = Decimal("0.00")

    # Costes de tokens LLM (viene de LLMUsageLog, ver capítulo 4)
    coste_tokens_eur: Decimal = Decimal("0.00")

    # Costes de infraestructura cloud (viene de CloudCostAgent, ver capítulo 12)
    coste_cloud_eur: Decimal = Decimal("0.00")

    # Herramientas SaaS y licencias
    coste_herramientas_eur: Decimal = Decimal("0.00")

    # Desglose por perfil de rol (para análisis)
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
        """Cuántas veces cuesta más el equipo que la IA."""
        if self.coste_tokens_eur == 0:
            return float("inf")
        return float(self.coste_personas_eur / self.coste_tokens_eur)


class TCOCalculator:
    """
    Calcula el TCO real de un proyecto integrando todas las fuentes de coste.
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
        Calcula el TCO completo de un proyecto en un rango de meses.

        Los costes de tokens y cloud se pasan como parámetros porque
        vienen de sistemas externos (LLMUsageLog, CloudCostAgent).
        El coste de personas se calcula internamente desde las imputaciones.
        """
        desglose = DesgloseTCO(
            proyecto_codigo=proyecto_codigo,
            mes_inicio=mes_inicio,
            mes_fin=mes_fin,
            coste_tokens_eur=coste_tokens_eur,
            coste_cloud_eur=coste_cloud_eur,
            coste_herramientas_eur=coste_herramientas_eur,
        )

        # Recuperar todas las imputaciones del proyecto en el período
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

        # Calcular coste total de personas y desglose por perfil
        for imp in imputaciones:
            coste_imp = imp.calcular_coste_mes()
            desglose.coste_personas_eur += coste_imp

            perfil_nombre = imp.perfil_coste.nombre
            if perfil_nombre not in desglose.desglose_por_perfil:
                desglose.desglose_por_perfil[perfil_nombre] = Decimal("0")
            desglose.desglose_por_perfil[perfil_nombre] += coste_imp

        return desglose
