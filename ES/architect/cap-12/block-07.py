# Extraído de: LibroTecnico/cap-12-rag-produccion.md
    # Enriquecimiento automático con IA (Claude/modelo configurado)
    ai_summary = Column(Text, nullable=True)         # Resumen ejecutivo generado
    ai_keywords = Column(JSON, nullable=True)         # Lista de palabras clave
    ai_entities = Column(JSON, nullable=True)         # Entidades detectadas (personas, org, fechas)
    ai_enriched_at = Column(DateTime, nullable=True)

    # Template reutilizable: el documento sirve como base para nuevos documentos
    is_template = Column(Boolean, default=False)
    template_variables = Column(JSON, nullable=True)  # Variables parametrizables

    # Propietario y control de acceso
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    allowed_roles = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relaciones de versiones
    child_versions = relationship(
        "Document",
        foreign_keys=[parent_version_id],
        backref="parent_version",
        lazy="dynamic",
    )
