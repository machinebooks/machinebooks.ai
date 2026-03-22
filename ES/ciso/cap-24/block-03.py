# Extraído de: LibroCISO/cap-24-calidad-ia.md
class BudgetConfig(Base):
    """Configuración de presupuestos y alertas de gasto IA.

    Permite definir límites globales, por servicio y por usuario.
    La acción al superar el límite es configurable: avisar,
    degradar a modelo más barato, o bloquear.
    """
    __tablename__ = 'budget_configs'

    id = Column(Integer, primary_key=True)

    # Límites globales (USD)
    monthly_budget_usd = Column(Float, nullable=True)
    daily_budget_usd = Column(Float, nullable=True)
    alert_threshold_pct = Column(Float, default=80.0)
    # Alerta al alcanzar el 80% del presupuesto mensual

    # Límites por servicio (JSON)
    # {"privacy_agent": 50.0, "risk_agent": 30.0, "copilot_chat": 100.0}
    service_limits = Column(JSON, default=dict)

    # Límites por usuario (USD/mes)
    per_user_monthly_limit = Column(Float, default=15.0)

    # Acción al superar el límite
    action_on_limit = Column(String(20), default='alert')
    # 'alert'    = solo notifica al admin
    # 'throttle' = degrada a modelo más barato (sonnet → haiku)
    # 'block'    = bloquea llamadas LLM hasta siguiente período

    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
