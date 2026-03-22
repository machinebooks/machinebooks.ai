# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
# [OK] Patrón correcto: generado con Claude después de proporcionar contexto explícito
# Prompt incluía: diagrama de dominios, lista de entidades por schema,
# requisitos de soft delete y auditoría, políticas de retención GDPR

class Proposal(db.Model):
    """Propuesta técnica — pertenece al dominio de negocio (operations_db).
    Relacionada con Client y Opportunity. Soft delete con pipeline GDPR."""
    __tablename__ = 'proposals'
    # Sin __bind_key__ → operations_db por defecto

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=True)
    proposal_type = db.Column(db.Enum(ProposalType), nullable=False)
    status = db.Column(db.Enum(ProposalStatus), nullable=False, default=ProposalStatus.DRAFT)
    created_by = db.Column(db.Integer, db.ForeignKey('platform_core.users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete GDPR-compatible
