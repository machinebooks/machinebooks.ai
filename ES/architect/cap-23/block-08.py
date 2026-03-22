# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
class CompetitorProfile(db.Model):
    """
    Perfil de competidor con análisis SWOT y clasificación tipológica.
    Los perfiles se actualizan manualmente o por importación Excel.
    """
    __tablename__ = 'competitor_profiles'
    __bind_key__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)

    # Tipo de competencia
    competitor_type = db.Column(
        db.Enum('direct', 'indirect', 'substitute', name='competitor_type'),
        nullable=False
    )

    # SWOT como JSON estructurado para facilitar renderizado en frontend
    strengths = db.Column(db.JSON, default=list)    # Lista de strings
    weaknesses = db.Column(db.JSON, default=list)
    opportunities = db.Column(db.JSON, default=list)
    threats = db.Column(db.JSON, default=list)

    # Áreas de solapamiento con nuestro portfolio
    overlap_service_lines = db.Column(db.JSON, default=list)
    overlap_sectors = db.Column(db.JSON, default=list)

    # Posicionamiento de precio relativo (-1=más barato, 0=similar, 1=más caro)
    price_positioning = db.Column(db.Integer, default=0)

    # Datos de inteligencia (no estructurados, para búsqueda)
    notes = db.Column(db.Text)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
