# Extraído de: LibroCyberrange/cap-12-sistema-ctf.md
import hashlib
import re
import secrets
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from backend.models import Challenge, ChallengeInstance

FLAG_PREFIX = "CYBERRANGE"


class DynamicFlagService:
    """Genera y valida flags únicas por usuario/challenge."""

    @staticmethod
    def generate_flag_for_instance(
        db: Session,
        instance: ChallengeInstance,
        force_new: bool = False
    ) -> Optional[str]:
        """
        Genera una flag única para un usuario/challenge.

        La flag combina:
        - SHA-256 del (user_id + challenge_id + vmid + timestamp)
        - 8 bytes aleatorios de secrets.token_hex

        Resultado: CYBERRANGE{a3f7b12c89d1e4f2_9e4d6a8b3c1f7e02}
        """
        # Si ya tiene flag y no se fuerza regeneración, reutilizar
        if instance.flag_value and not force_new:
            return instance.flag_value

        # Componente determinista: hash del contexto del usuario
        timestamp = int(datetime.utcnow().timestamp())
        seed = (
            f"{instance.user_id}_"
            f"{instance.challenge_id}_"
            f"{instance.vmid or 0}_"
            f"{timestamp}"
        )
        hash_seed = hashlib.sha256(seed.encode()).hexdigest()[:16]

        # Componente aleatorio: imposible de predecir
        random_component = secrets.token_hex(8)

        # Flag final: prefijo + hash + random
        flag = f"{FLAG_PREFIX}{{{hash_seed}_{random_component}}}"

        # Persistir en la instancia del usuario
        instance.flag_value = flag
        instance.hash_seed = hash_seed
        db.commit()

        return flag

    @staticmethod
    def validate_dynamic_flag(
        db: Session,
        user_flag: str,
        user_id: int,
        challenge_id: int
    ) -> Dict[str, Any]:
        """
        Valida una flag dinámica comparando contra la instancia
        activa del usuario.
        """
        instance = db.query(ChallengeInstance).filter_by(
            user_id=user_id,
            challenge_id=challenge_id,
            state='open'
        ).first()

        if not instance or not instance.flag_value:
            return {
                'valid': False,
                'message': 'No hay flag activa para este challenge',
                'points': 0
            }

        # Extraer contenido entre llaves para comparación normalizada
        def _extract_content(f: str) -> str:
            f = f.strip().lower()
            m = re.match(r'^(\w+)\{(.+)\}$', f)
            return m.group(2) if m else f

        # Comparación timing-safe para evitar ataques de temporización
        import hmac
        is_valid = hmac.compare_digest(
            _extract_content(user_flag),
            _extract_content(instance.flag_value)
        )

        if is_valid:
            challenge = db.query(Challenge).filter_by(
                id=challenge_id
            ).first()
            points = challenge.max_points if challenge else 100

            instance.state = 'done'
            instance.completed_at = datetime.utcnow()
            instance.score = points
            db.commit()

            return {
                'valid': True,
                'message': 'Flag correcta',
                'points': points
            }

        return {
            'valid': False,
            'message': 'Flag incorrecta',
            'points': 0
        }
