# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/models/budget_config.py
class BudgetConfig(Base):
    """
    Límites de gasto con acciones graduadas.
    Progresión: alert → throttle → block
    """
    __tablename__ = "budget_config"

    id = Column(Integer, primary_key=True)
    scope = Column(String(16))    # "global", "provider", "service", "user"
    scope_id = Column(String(64)) # ID del proveedor/servicio/usuario

    # Límites en EUR
    daily_limit_eur = Column(Float)
    monthly_limit_eur = Column(Float)
    per_user_daily_limit_eur = Column(Float)

    # Umbrales para acciones (porcentaje del límite)
    alert_threshold_pct = Column(Float, default=80.0)     # Envía alerta
    throttle_threshold_pct = Column(Float, default=95.0)  # Reduce rate
    block_threshold_pct = Column(Float, default=100.0)    # Bloquea

    # Configuración de throttle: ralentizar sin bloquear
    throttle_delay_seconds = Column(Float, default=2.0)
    throttle_max_concurrent = Column(Integer, default=3)

    is_active = Column(Boolean, default=True)
    notify_emails = Column(JSON)  # Lista de emails para alertas
