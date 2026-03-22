# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
# Modelos SQLAlchemy para el schema analytics_db
# Cada modelo declara __bind_key__ = 'analytics' para que
# SQLAlchemy sepa a qué schema de conexión pertenece
# 'analytics' es el bind_key de SQLAlchemy que mapea al schema analytics_db

class HeatmapScore(db.Model):
    """
    Almacena el scoring multidimensional precalculado
    para la matriz Sector × Línea de servicio.
    Los scores se recalculan por workers Celery según configuración.
    """
    __tablename__ = 'heatmap_scores'
    __bind_key__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    sector_id = db.Column(db.Integer, nullable=False, index=True)
    service_line_id = db.Column(db.Integer, nullable=False, index=True)

    # Score final ponderado (0-100)
    total_score = db.Column(db.Float, nullable=False)

    # Subscores por dimensión (0-100 cada uno)
    score_demand = db.Column(db.Float, default=0.0)       # Demanda: 30%
    score_traction = db.Column(db.Float, default=0.0)     # Tracción: 20%
    score_economic = db.Column(db.Float, default=0.0)     # Económico: 25%
    score_right_to_win = db.Column(db.Float, default=0.0) # RTW: 25%

    # Datos raw que alimentaron el cálculo (para auditabilidad)
    opportunities_count = db.Column(db.Integer, default=0)
    pipeline_volume = db.Column(db.Float, default=0.0)
    installed_base_volume = db.Column(db.Float, default=0.0)
    avg_margin_pct = db.Column(db.Float, default=0.0)
    win_rate_pct = db.Column(db.Float, default=0.0)

    # Control de vigencia del cálculo
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    period = db.Column(db.String(7), nullable=False)  # 'YYYY-MM'

    __table_args__ = (
        db.UniqueConstraint('sector_id', 'service_line_id', 'period',
                           name='uq_heatmap_sector_service_period'),
        db.Index('ix_heatmap_period_score', 'period', 'total_score'),
    )
