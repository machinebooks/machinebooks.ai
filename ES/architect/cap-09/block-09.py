# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: servicio de notificaciones
# Patrón: backend/services/notifications/notification_service.py

class NotificationService:
    """Servicio centralizado de generación y entrega de notificaciones."""

    PRIORITY_MAP = {
        "NEW_OPPORTUNITY":   "HIGH",
        "OPPORTUNITY_MATCH": "HIGH",
        "DEAL_STALLED":      "MEDIUM",
        "ACCOUNT_RISK":      "HIGH",
        "REPORT_READY":      "MEDIUM",
        "SYSTEM":            "LOW",
    }

    @classmethod
    def send(
        cls,
        user_id: int,
        notification_type: str,
        title: str,
        body: str,
        action_url: str = None,
        extra_data: dict = None,
        priority: str = None,
    ) -> Optional["Notification"]:
        """
        Genera una notificación, evitando duplicados activos.
        Registra en base de datos y puede enviar email si la prioridad es HIGH.
        """
        # Comprobar duplicado activo
        existing = Notification.query.filter_by(
            user_id=user_id,
            notification_type=notification_type,
            action_url=action_url,
            is_read=False
        ).first()

        if existing:
            return None  # Ya existe notificación activa para este recurso

        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            priority=priority or cls.PRIORITY_MAP.get(notification_type, "MEDIUM"),
            action_url=action_url,
            extra_data=extra_data or {},
        )
        db.session.add(notification)
        db.session.commit()

        # Envío por email para notificaciones de prioridad alta
        if notification.priority == "HIGH":
            celery_app.send_task(
                "tasks.notifications.send_email_notification",
                args=[notification.id],
                queue="default"
            )

        return notification
