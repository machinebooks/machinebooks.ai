# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/mfa_handler.py

import redis
import json
import time
from datetime import datetime, timedelta
from celery import Task

class MFAWaitMixin:
    """Mixin para gestionar esperas de segundo factor en bots de automatización.

    El bot publica el estado MFA_PENDING en Redis y espera hasta que
    el usuario proporcione el código o expire el timeout.
    """

    MFA_TIMEOUT_SECONDS = 300   # 5 minutos para que el humano proporcione el código
    MFA_POLL_INTERVAL = 2       # Comprueba Redis cada 2 segundos

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def request_mfa_code(self, task_id: str, system_name: str, user_id: int) -> str | None:
        """Publica el estado MFA_PENDING y espera el código del usuario.

        Returns:
            El código OTP proporcionado por el usuario, o None si expiró.
        """
        mfa_key = f"mfa:pending:{task_id}"
        expires_at = datetime.utcnow() + timedelta(seconds=self.MFA_TIMEOUT_SECONDS)

        # Publicar estado de espera en Redis
        mfa_state = {
            "status": "pending",
            "system": system_name,
            "task_id": task_id,
            "expires_at": expires_at.isoformat(),
            "code": None
        }
        self.redis.setex(
            mfa_key,
            self.MFA_TIMEOUT_SECONDS + 60,  # TTL con margen
            json.dumps(mfa_state)
        )

        # Notificar al usuario que el bot está esperando
        self._notify_user_mfa_required(user_id, task_id, system_name, expires_at)
