# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Registro de intentos de login — siempre registra, éxito o fallo
# Fichero: cyber-range-builder/backend/services/audit_service.py

class AuditService:
    @staticmethod
    def log_login_attempt(
        db: Session,
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Registra intento de login con contexto completo.
        Los intentos fallidos se registran con severity 'warning'
        para facilitar la detección de fuerza bruta."""
        return AuditService.log_event(
            db=db,
            event_type='login_attempt',
            category='authentication',
            action='login_attempt',
            description=f"Intento de login "
                        f"{'exitoso' if success else 'fallido'} "
                        f"para usuario {username}",
            severity='info' if success else 'warning',
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            status='success' if success else 'failure',
            error_message=failure_reason,
            request_id=request_id,
            module='auth',
            function='login',
            details={
                'success': success,
                'failure_reason': failure_reason,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
