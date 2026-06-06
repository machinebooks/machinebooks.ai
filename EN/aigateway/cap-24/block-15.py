# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# gateway/app/models/hook.py: delivery log (synthetic)
class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id                = Column(Integer, primary_key=True)
    webhook_config_id = Column(Integer, ForeignKey("webhook_configs.id"))
    event_key         = Column(String(128), nullable=False)
    status_code       = Column(Integer)            # receiver HTTP status (NULL if no response)
    duration_ms       = Column(Float)              # how long the delivery took
    error             = Column(Text)               # message if it failed (timeout, connection, 5xx)
    created_at        = Column(DateTime, default=utcnow)
