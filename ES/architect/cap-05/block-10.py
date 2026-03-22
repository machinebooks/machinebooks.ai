# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
# [ANTI-PATRON] schema "plano" generado sin contexto de dominio
# Claude optimizó para simplicidad; el resultado es técnicamente válido
# pero semánticamente incorrecto para el negocio real

class ProposalSystem(db.Model):
    """Modelo generado por Claude sin contexto de dominio suficiente.
    Mezcla datos de negocio, plataforma y analytics en una sola tabla."""
    __tablename__ = 'proposal_system'  # Nombre genérico sin significado de dominio

    id = db.Column(db.Integer, primary_key=True)

    # Datos de negocio — deberían estar en operations_db
    client_name = db.Column(db.String(200))    # Sin FK a tabla de clientes
    proposal_text = db.Column(db.Text)          # Texto libre sin estructura
    status = db.Column(db.String(20))           # Sin enum, cualquier string

    # Datos de plataforma — deberían estar en platform_core
    created_by = db.Column(db.String(100))      # Nombre de usuario en texto, sin FK
    ai_model_used = db.Column(db.String(50))    # Sin vínculo a LLMServiceConfig

    # Datos de analytics — deberían estar en analytics_db
    view_count = db.Column(db.Integer, default=0)  # Métrica mezclada con dato operativo
    last_viewed = db.Column(db.DateTime)

    # Sin índices explícitos
    # Sin soft delete
    # Sin auditoría
    # Sin timestamps de creación/modificación
