# Extraído de: LibroPQC/cap-23-observabilidad.md
def to_dict(self):
    """Serialización con resolución de nombre de usuario.
    Si el usuario fue eliminado, muestra 'Sistema'."""
    return {
        'id': self.id,
        'user_id': self.user_id,
        'user_name': (
            (self.user.full_name or self.user.username)
            if self.user else 'Sistema'
        ),
        'user_email': self.user.email if self.user else None,
        'action': self.action,
        'entity_type': self.entity_type,
        'entity_id': self.entity_id,
        'details': self.details,
        'ip_address': self.ip_address,
        'user_agent': self.user_agent,
        'created_at': (
            self.created_at.isoformat()
            if self.created_at else None
        ),
    }
