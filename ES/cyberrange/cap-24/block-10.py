# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Estadísticas del dashboard de auditoría
# Fichero: cyber-range-builder/backend/services/audit_service.py

@staticmethod
def get_dashboard_stats(db: Session) -> AuditDashboardStats:
    """Estadísticas operativas calculadas en tiempo real.
    Incluye: eventos del día, errores, eventos de seguridad,
    intentos de login, top usuarios, top acciones, distribución temporal."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())

    # Métricas básicas del día
    total_events_today = db.query(AuditLog).filter(
        AuditLog.timestamp >= today_start
    ).count()

    total_errors_today = db.query(AuditLog).filter(
        and_(AuditLog.timestamp >= today_start,
             AuditLog.severity.in_(['error', 'critical']))
    ).count()

    total_security_events_today = db.query(AuditLog).filter(
        and_(AuditLog.timestamp >= today_start,
             or_(AuditLog.event_type == 'security_event',
                 AuditLog.severity == 'security'))
    ).count()

    # Distribución temporal: eventos por hora (últimas 24h)
    events_by_hour = []
    for i in range(24):
        hour_start = datetime.utcnow() - timedelta(hours=i+1)
        hour_end = datetime.utcnow() - timedelta(hours=i)
        count = db.query(AuditLog).filter(
            and_(AuditLog.timestamp >= hour_start,
                 AuditLog.timestamp < hour_end)
        ).count()
        events_by_hour.append({
            'hour': hour_start.strftime('%H:00'),
            'count': count
        })

    # Top 10 usuarios por actividad
    top_users_by_activity = db.query(
        AuditLog.username,
        func.count(AuditLog.id).label('event_count')
    ).filter(
        and_(AuditLog.timestamp >= today_start,
             AuditLog.username.isnot(None))
    ).group_by(AuditLog.username).order_by(
        desc('event_count')
    ).limit(10).all()

    # ... más métricas: top acciones, top errores,
    # distribución por categoría y por severidad
