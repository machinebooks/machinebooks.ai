# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# gateway/app/models/hook.py (synthetic)
class WebhookConfig(Base):
    __tablename__ = "webhook_configs"

    id                   = Column(Integer, primary_key=True)
    organization_id      = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # NULL = global
    url                  = Column(String(2048), nullable=False)   # POST destination
    secret               = Column(String(256), nullable=False)    # HMAC signing key
    events               = Column(JSON, nullable=False)           # ["deployment.degraded", ...]
    is_active            = Column(Boolean, default=True)
    consecutive_failures = Column(Integer, default=0)             # auto-disable from 5 onward
