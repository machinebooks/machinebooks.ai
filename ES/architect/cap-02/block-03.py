# Extraído de: LibroTecnico/cap-02-arquitecto-ia-claude.md
from datetime import datetime, timezone

class UserMemory(db.Model):
    """Memoria persistente del usuario para el Copilot IA.

    Permite al asistente recordar preferencias, hechos sobre clientes,
    patrones de trabajo e insights entre sesiones distintas.
    Máximo 50 memorias activas por usuario (se desactivan las menos
    usadas cuando se supera el límite — requerimiento de rendimiento
    y control de contexto en el system prompt).
    """
    __tablename__ = 'user_memories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    category = db.Column(db.String(50), nullable=False)
    # Valores válidos: preference, client_fact, workflow, insight
    content = db.Column(db.Text, nullable=False)
    source = db.Column(
        db.String(20),
        default='auto_extracted'
    )
    # auto_extracted: generada por el asistente | manual: creada por el usuario
    use_count = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    # Soft delete para GDPR (derecho de borrado sin perder histórico)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relación con el usuario
    user = db.relationship('User', back_populates='memories')

    # Índice compuesto para queries habituales
    # (get_active_memories_for_user filtra user_id + is_active + category)
    __table_args__ = (
        db.Index(
            'idx_user_memory_active',
            'user_id', 'is_active', 'category'
        ),
    )

    def to_dict(self, include_sensitive=False):
        return {
            'id': self.id,
            'category': self.category,
            'content': self.content,
            'source': self.source,
            'use_count': self.use_count,
            'last_used_at': (
                self.last_used_at.isoformat()
                if self.last_used_at else None
            ),
            'created_at': self.created_at.isoformat(),
        }
