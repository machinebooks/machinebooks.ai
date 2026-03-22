# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Detección automatizada de amenazas
# Fichero: cyber-range-builder/backend/services/audit_service.py

class AuditService:
    @staticmethod
    def log_event(db, ...):
        # ... registro del evento ...

        # Procesamiento asíncrono para eventos críticos
        if severity in ['security', 'critical'] or event_type == 'security_event':
            asyncio.create_task(
                AuditService._process_security_event(audit_log.id, db)
            )
        return audit_log

    @staticmethod
    async def _process_security_event(audit_log_id: int, db: Session):
        """Analiza eventos de seguridad en background para detectar patrones:
        - Múltiples intentos de login fallidos desde la misma IP
        - Acceso a endpoints de admin desde roles no autorizados
        - Ráfagas de peticiones que sugieren escaneo automatizado
        - Acceso a recursos fuera de la workzone asignada"""
        try:
            log = db.query(AuditLog).get(audit_log_id)
            if not log:
                return

            # Patrón 1: Fuerza bruta — 10+ intentos fallidos
            # desde la misma IP en los últimos 15 minutos
            if log.event_type == 'login_attempt' and log.status == 'failure':
                cutoff = datetime.utcnow() - timedelta(minutes=15)
                failed_count = db.query(AuditLog).filter(
                    and_(
                        AuditLog.event_type == 'login_attempt',
                        AuditLog.status == 'failure',
                        AuditLog.ip_address == log.ip_address,
                        AuditLog.timestamp >= cutoff
                    )
                ).count()

                if failed_count >= 10:
                    AuditService.log_event(
                        db=db,
                        event_type='security_event',
                        category='security',
                        action='brute_force_detected',
                        description=f"Posible ataque de fuerza bruta desde "
                                    f"{log.ip_address}: {failed_count} "
                                    f"intentos fallidos en 15 minutos",
                        severity='critical',
                        ip_address=log.ip_address,
                        module='threat_detection',
                        function='_process_security_event',
                        tags=['brute_force', 'automated_detection']
                    )

            # Patrón 2: Escalada de privilegios — acceso denegado
            # repetido a recursos de admin
            if log.action in ['view_admin_dashboard', 'modify_config'] \
               and log.status == 'failure':
                cutoff = datetime.utcnow() - timedelta(minutes=30)
                denied_count = db.query(AuditLog).filter(
                    and_(
                        AuditLog.user_id == log.user_id,
                        AuditLog.status == 'failure',
                        AuditLog.category == 'authorization',
                        AuditLog.timestamp >= cutoff
                    )
                ).count()

                if denied_count >= 5:
                    AuditService.log_event(
                        db=db,
                        event_type='security_event',
                        category='security',
                        action='privilege_escalation_attempt',
                        description=f"Posible intento de escalada de privilegios "
                                    f"del usuario {log.username}: {denied_count} "
                                    f"accesos denegados en 30 minutos",
                        severity='security',
                        user_id=log.user_id,
                        username=log.username,
                        ip_address=log.ip_address,
                        module='threat_detection',
                        function='_process_security_event',
                        tags=['privilege_escalation', 'automated_detection']
                    )

            # Patrón 3: Escaneo de endpoints — peticiones a rutas
            # que no existen o que devuelven 404 repetidamente
            if log.status == 'failure' and log.error_code == '404':
                cutoff = datetime.utcnow() - timedelta(minutes=5)
                scan_count = db.query(AuditLog).filter(
                    and_(
                        AuditLog.ip_address == log.ip_address,
                        AuditLog.error_code == '404',
                        AuditLog.timestamp >= cutoff
                    )
                ).count()

                if scan_count >= 20:
                    AuditService.log_event(
                        db=db,
                        event_type='security_event',
                        category='security',
                        action='endpoint_scanning_detected',
                        description=f"Posible escaneo de endpoints desde "
                                    f"{log.ip_address}: {scan_count} "
                                    f"peticiones a rutas inexistentes en 5 min",
                        severity='warning',
                        ip_address=log.ip_address,
                        module='threat_detection',
                        function='_process_security_event',
                        tags=['scanning', 'automated_detection']
                    )

        except Exception as e:
            logger.error(
                f"Error procesando evento de seguridad {audit_log_id}: {str(e)}"
            )
