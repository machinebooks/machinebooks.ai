# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# gateway/app/models/hook.py: log de entregas (sintético)
class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id                = Column(Integer, primary_key=True)
    webhook_config_id = Column(Integer, ForeignKey("webhook_configs.id"))
    event_key         = Column(String(128), nullable=False)
    status_code       = Column(Integer)            # status HTTP del receptor (NULL si no respondió)
    duration_ms       = Column(Float)              # cuánto tardó la entrega
    error             = Column(Text)               # mensaje si falló (timeout, conexión, 5xx)
    created_at        = Column(DateTime, default=utcnow)
