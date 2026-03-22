# Extraído de: LibroFinOps/cap-11-presupuestos-circuit-breakers.md
# services/financial_circuit_breaker.py
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import threading
import logging

logger = logging.getLogger(__name__)

class CircuitState(str, Enum):
    CLOSED    = "closed"     # operación normal
    OPEN      = "open"       # spike detectado, rechazando peticiones
    HALF_OPEN = "half_open"  # periodo de prueba

@dataclass
class SpendRecord:
    """Registro de gasto para la ventana deslizante."""
    timestamp: datetime
    cost_usd:  float

class ProviderCircuitBreaker:
    """
    Circuit breaker financiero para un proveedor LLM.

    Abre cuando la velocidad de consumo supera N veces la media histórica.
    Protege contra bugs de bucle y errores de configuración que generan
    spikes de gasto en minutos, no en horas.
    """

    def __init__(
        self,
        provider_name: str,
        # Ventana de observación para calcular la velocidad de consumo
        window_minutes: int = 10,
        # Múltiplo de la media histórica que activa la apertura
        spike_multiplier: float = 5.0,
        # Gasto mínimo para activar (evitar falsos positivos con costes bajos)
        min_spend_to_open_usd: float = 1.0,
        # Tiempo de espera antes de pasar a HALF_OPEN
        open_timeout_seconds: int = 300,  # 5 minutos
    ):
        self.provider_name        = provider_name
        self.window_minutes       = window_minutes
        self.spike_multiplier     = spike_multiplier
        self.min_spend_to_open    = min_spend_to_open_usd
        self.open_timeout         = open_timeout_seconds

        self._state               = CircuitState.CLOSED
        self._spend_window: deque = deque()  # registros en la ventana
        self._historical_rate     = 0.0  # USD/minuto media histórica
        self._opened_at: datetime | None = None
        self._lock                = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Devuelve el estado actual, transitando a HALF_OPEN si procede."""
        with self._lock:
            if (self._state == CircuitState.OPEN
                    and self._opened_at is not None
                    and (datetime.utcnow() - self._opened_at).seconds >= self.open_timeout):
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker %s → HALF_OPEN", self.provider_name)
            return self._state

    def allow_request(self) -> bool:
        """
        ¿Debe permitirse esta petición?
        CLOSED y HALF_OPEN permiten; OPEN rechaza.

        Thread-safe: adquiere el lock y verifica la transición OPEN->HALF_OPEN
        de forma atómica.
        """
        with self._lock:
            state = self._state
            # Verificar transición OPEN -> HALF_OPEN dentro del lock
            if (state == CircuitState.OPEN
                    and self._opened_at is not None
                    and (datetime.utcnow() - self._opened_at).seconds >= self.open_timeout):
                self._state = CircuitState.HALF_OPEN
                state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker %s → HALF_OPEN", self.provider_name)

        if state == CircuitState.OPEN:
            logger.warning("Circuit breaker OPEN: rechazando petición a %s",
                           self.provider_name)
            return False
        return True

    def record_success(self, cost_usd: float):
        """
        Registra una llamada exitosa y comprueba si hay spike.
        Debe llamarse DESPUÉS de cada llamada LLM para actualizar la ventana.
        """
        with self._lock:
            now = datetime.utcnow()

            # Añadir a la ventana deslizante
            self._spend_window.append(SpendRecord(timestamp=now, cost_usd=cost_usd))

            # Limpiar registros fuera de la ventana
            cutoff = now - timedelta(minutes=self.window_minutes)
            while self._spend_window and self._spend_window[0].timestamp < cutoff:
                self._spend_window.popleft()

            # Calcular velocidad actual (USD/minuto en la ventana)
            window_spend = sum(r.cost_usd for r in self._spend_window)
            current_rate = window_spend / self.window_minutes

            # Si estábamos en HALF_OPEN y el coste es normal, cerrar
            if self._state == CircuitState.HALF_OPEN:
                if current_rate <= self._historical_rate * self.spike_multiplier:
                    self._state = CircuitState.CLOSED
                    logger.info("Circuit breaker %s → CLOSED (recuperado)",
                                self.provider_name)
                else:
                    self._state = CircuitState.OPEN
                    self._opened_at = now
                    return

            # Actualizar media histórica (media móvil exponencial suavizada)
            if self._historical_rate == 0:
                self._historical_rate = current_rate
            else:
                alpha = 0.1  # factor de suavizado: 10% nueva observación
                self._historical_rate = (
                    alpha * current_rate
                    + (1 - alpha) * self._historical_rate
                )

            # Comprobar si hay spike
            if (current_rate > self._historical_rate * self.spike_multiplier
                    and window_spend >= self.min_spend_to_open):
                self._state     = CircuitState.OPEN
                self._opened_at = now
                logger.error(
                    "Circuit breaker %s ABIERTO: tasa actual=$%.4f/min, "
                    "media histórica=$%.4f/min, factor=%.1fx",
                    self.provider_name, current_rate,
                    self._historical_rate, self.spike_multiplier,
                )

    def record_failure(self):
        """Registra un fallo del proveedor (para métricas, no afecta al estado financiero)."""
        logger.warning("Fallo registrado en %s", self.provider_name)
