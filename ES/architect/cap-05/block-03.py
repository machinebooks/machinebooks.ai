# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
import enum

class ProposalType(enum.Enum):
    BASE       = "base"
    COMPETITIVE = "competitive"
    PREMIUM    = "premium"
    CUSTOM     = "custom"
    EXECUTIVE  = "executive"

class ProposalStatus(enum.Enum):
    DRAFT      = "draft"
    IN_REVIEW  = "in_review"
    APPROVED   = "approved"
    REJECTED   = "rejected"
    SENT       = "sent"
    WON        = "won"
    LOST       = "lost"

class Proposal(db.Model):
    """Propuesta técnica generada para una oportunidad.
    Un proyecto puede tener múltiples propuestas en distintos estados."""
    __tablename__ = 'proposals'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=True)

    proposal_type = db.Column(db.Enum(ProposalType), nullable=False, default=ProposalType.BASE)
    status = db.Column(db.Enum(ProposalStatus), nullable=False, default=ProposalStatus.DRAFT)

    title = db.Column(db.String(300), nullable=False)
    executive_summary = db.Column(db.Text)

    # Metadatos de generación IA — trazabilidad de qué modelo lo generó
    ai_generated = db.Column(db.Boolean, default=False)
    ai_model_used = db.Column(db.String(100))         # claude-sonnet-4-6
    ai_generation_tokens = db.Column(db.Integer)      # coste de la generación
    ai_generation_cost_eur = db.Column(db.Float)

    # Campos de auditoría
    created_by = db.Column(db.Integer, db.ForeignKey('platform_core.users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.Index('idx_proposal_project_status', 'project_id', 'status'),
        db.Index('idx_proposal_type_created', 'proposal_type', 'created_at'),
    )
