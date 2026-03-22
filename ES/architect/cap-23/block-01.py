# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
class FunnelStage(db.Model):
    """
    Snapshot del embudo de ventas por etapa.
    Materializado desde operations_db por workers programados.
    F1=Discovery, F2=Qualification, F3=Proposal, F4=Negotiation, F5=Won
    """
    __tablename__ = 'funnel_stages'
    __bind_key__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.String(2), nullable=False)       # F1-F5
    stage_name = db.Column(db.String(50), nullable=False)
    opportunity_count = db.Column(db.Integer, default=0)
    total_value = db.Column(db.Float, default=0.0)
    avg_days_in_stage = db.Column(db.Float, default=0.0)
    conversion_rate = db.Column(db.Float, default=0.0)    # 0.0-1.0
    period = db.Column(db.String(7), nullable=False)

    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
