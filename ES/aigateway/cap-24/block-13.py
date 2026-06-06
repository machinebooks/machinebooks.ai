# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# gateway/app/models/hook.py (sintético)
class WebhookConfig(Base):
    __tablename__ = "webhook_configs"

    id                   = Column(Integer, primary_key=True)
    organization_id      = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # NULL = global
    url                  = Column(String(2048), nullable=False)   # destino del POST
    secret               = Column(String(256), nullable=False)    # clave de firma HMAC
    events               = Column(JSON, nullable=False)           # ["deployment.degraded", ...]
    is_active            = Column(Boolean, default=True)
    consecutive_failures = Column(Integer, default=0)             # auto-disable a partir de 5
