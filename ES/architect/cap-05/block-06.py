# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
class LLMModelPricing(db.Model):
    """Precios por token configurables desde el panel de Admin.
    Permite calcular costes automáticamente por tarea y por proveedor."""
    __tablename__ = 'llm_model_pricing'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(30), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    input_price_per_1k = db.Column(db.Float, nullable=False)   # EUR/1.000 tokens de entrada
    output_price_per_1k = db.Column(db.Float, nullable=False)  # EUR/1.000 tokens de salida
    currency = db.Column(db.String(3), default='EUR')          # ISO 4217
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    effective_from = db.Column(db.DateTime, nullable=False)    # Historial de cambios de precio
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('provider', 'model_name', 'effective_from',
                            name='uq_pricing_provider_model_date'),
    )
