# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: backoff exponencial con jitter
# Patrón: tasks/utils/retry.py

import random

def exponential_backoff_with_jitter(
    retry_number: int,
    base_delay: int = 60,
    max_delay: int = 3600,
    jitter_factor: float = 0.25,
) -> int:
    """
    Calcula el tiempo de espera con backoff exponencial y jitter.

    Fórmula: delay = min(base * 2^retry, max) * (1 + random(-jitter, +jitter))

    Con base=60 y jitter=0.25:
      - Reintento 1: entre 45s y 75s   (60 ± 25%)
      - Reintento 2: entre 90s y 150s  (120 ± 25%)
      - Reintento 3: entre 180s y 300s (240 ± 25%)
      - Reintento 4: entre 360s y 600s (480 ± 25%)
    """
    # Base exponencial con techo máximo
    base_wait = min(base_delay * (2 ** retry_number), max_delay)

    # Jitter: desplazar aleatoriamente entre -25% y +25%
    jitter = base_wait * jitter_factor * (2 * random.random() - 1)

    return max(1, int(base_wait + jitter))


# Uso en una tarea AITask:
# raise self.retry(exc=exc, countdown=exponential_backoff_with_jitter(
#     self.request.retries
# ))
