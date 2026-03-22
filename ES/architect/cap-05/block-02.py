# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
class Client(db.Model):
    """Cliente de la Plataforma. Punto de entrada del dominio de negocio."""
    __tablename__ = 'clients'
    # Sin __bind_key__ → va a operations_db (bind por defecto)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    sector = db.Column(db.String(100))
    # Sector como string libre para flexibilidad; enum cuando el catálogo
    # esté estabilizado y validado con el negocio
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

    # Relaciones — un cliente tiene múltiples proyectos
    projects = db.relationship('Project', backref='client', lazy='dynamic')

    # Soft delete: nunca borramos un cliente, lo desactivamos
    # El campo es nullable: NULL significa "activo", datetime significa "eliminado"
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Client id={self.id} name={self.name!r}>'
