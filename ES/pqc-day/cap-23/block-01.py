# Extraído de: LibroPQC/cap-23-observabilidad.md
@staticmethod
def log(user_id, action, entity_type=None, entity_id=None,
        details=None, ip_address=None, user_agent=None):
    """Crea un registro de auditoría y lo persiste.
    Uso: AuditLog.log(user.id, 'create_client',
         entity_type='client', entity_id=nuevo_cliente.id,
         details={'name': 'Entidad Financiera'},
         ip_address=request.remote_addr,
         user_agent=request.headers.get('User-Agent'))
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.session.add(entry)
    db.session.commit()
    return entry
