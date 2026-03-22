# Source: The FinOps Engineer and the Machine -- Chapter 28
# Pattern: Agent session model with cost tracking

# models/agent_session.py
# Agent session with integrated total cost tracking.

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from database import Base


class AgentSession(Base):
    """
    Work session for a co-pilot agent.
    The total_cost_eur field accumulates the cost of all LLM calls,
    including delegated sub-agents. This is the minimum viable FinOps
    pattern for agents: a field that grows with each call and that
    the system checks before authorizing the next one.
    """
    __tablename__ = "agent_session"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, nullable=False)
    usuario_codigo = Column(String(50), nullable=False)
    agente_tipo = Column(String(100), nullable=False)
    objetivo = Column(String(500))

    # Financial control
    presupuesto_eur = Column(Numeric(10, 6), nullable=True)
    total_cost_eur = Column(Numeric(10, 6), default=Decimal("0.000000"))
    num_llamadas_llm = Column(Integer, default=0)

    estado = Column(String(50), default="activa")
    razon_detencion = Column(String(200), nullable=True)
    iniciada_en = Column(DateTime, default=datetime.utcnow)
    completada_en = Column(DateTime, nullable=True)

    def registrar_llamada(self, coste_eur: Decimal) -> bool:
        """
        Record the cost of a call.
        Returns True if the session can continue, False if it should stop.
        """
        self.total_cost_eur += coste_eur
        self.num_llamadas_llm += 1

        if self.presupuesto_eur and self.total_cost_eur > self.presupuesto_eur:
            self.estado = "stopped_by_budget"
            self.razon_detencion = (
                f"Cost €{float(self.total_cost_eur):.4f} exceeds "
                f"budget €{float(self.presupuesto_eur):.4f}"
            )
            self.completada_en = datetime.utcnow()
            return False

        return True

    @property
    def pct_presupuesto_utilizado(self) -> float:
        if not self.presupuesto_eur or self.presupuesto_eur == 0:
            return 0.0
        return float(self.total_cost_eur / self.presupuesto_eur * 100)
