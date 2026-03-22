# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
        # Polling hasta obtener el código o agotar el timeout
        deadline = time.time() + self.MFA_TIMEOUT_SECONDS
        while time.time() < deadline:
            state_raw = self.redis.get(mfa_key)
            if state_raw:
                state = json.loads(state_raw)
                if state.get("code"):
                    # Usuario proporcionó el código
                    self.redis.delete(mfa_key)
                    return state["code"]
            time.sleep(self.MFA_POLL_INTERVAL)

        # Timeout: limpiar el estado y devolver None
        self.redis.delete(mfa_key)
        return None

    def _notify_user_mfa_required(
        self, user_id: int, task_id: str, system: str, expires_at: datetime
    ):
        """Envía notificación al usuario a través del sistema de la Plataforma."""
        # Publicar en Redis para que el servicio de notificaciones lo recoja
        notification = {
            "type": "SYSTEM",
            "priority": "HIGH",
            "user_id": user_id,
            "title": f"Código MFA requerido — {system}",
            "message": (
                f"El bot de automatización necesita el código de doble factor "
                f"para continuar. Tienes hasta {expires_at.strftime('%H:%M')} "
                f"para proporcionarlo."
            ),
            "action_url": f"/admin/automation/tasks/{task_id}/mfa",
            "extra_data": {"task_id": task_id, "system": system}
        }
        self.redis.lpush("notifications:pending", json.dumps(notification))
