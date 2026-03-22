# Extraído de: LibroFinOps/cap-28-finops-agentes-autonomos.md
# models/agent_session.py
# Sesión de agente con tracking de coste total integrado.

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from database import Base


class AgentSession(Base):
    """
    Sesión de trabajo de un agente co-piloto.
    El campo total_cost_eur acumula el coste de todas las llamadas LLM,
    incluyendo sub-agentes delegados. Es el patrón mínimo viable
    de FinOps en agentes: un campo que crece con cada llamada y que
    el sistema verifica antes de autorizar la siguiente.
    """
    __tablename__ = "agent_session"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, nullable=False)
    usuario_codigo = Column(String(50), nullable=False)
    agente_tipo = Column(String(100), nullable=False)
    objetivo = Column(String(500))

    # Control financiero
    presupuesto_eur = Column(Numeric(10, 6), nullable=True)
    total_cost_eur = Column(Numeric(10, 6), default=Decimal("0.000000"))
    num_llamadas_llm = Column(Integer, default=0)

    estado = Column(String(50), default="activa")
    razon_detencion = Column(String(200), nullable=True)
    iniciada_en = Column(DateTime, default=datetime.utcnow)
    completada_en = Column(DateTime, nullable=True)

    def registrar_llamada(self, coste_eur: Decimal) -> bool:
        """
        Registra el coste de una llamada.
        Returns True si la sesión puede continuar, False si debe detenerse.
        """
        self.total_cost_eur += coste_eur
        self.num_llamadas_llm += 1

        if self.presupuesto_eur and self.total_cost_eur > self.presupuesto_eur:
            self.estado = "detenida_por_presupuesto"
            self.razon_detencion = (
                f"Coste €{float(self.total_cost_eur):.4f} supera "
                f"presupuesto €{float(self.presupuesto_eur):.4f}"
            )
            self.completada_en = datetime.utcnow()
            return False

        return True

    @property
    def pct_presupuesto_utilizado(self) -> float:
        if not self.presupuesto_eur or self.presupuesto_eur == 0:
            return 0.0
        return float(self.total_cost_eur / self.presupuesto_eur * 100)
