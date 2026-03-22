# Source: The FinOps Engineer and the Machine -- Chapter 11
# Pattern: Financial circuit breaker (open/half-open/closed)

# services/financial_circuit_breaker.py
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import threading
import logging

logger = logging.getLogger(__name__)

class CircuitState(str, Enum):
    CLOSED    = "closed"     # normal operation
    OPEN      = "open"       # spike detected, rejecting requests
    HALF_OPEN = "half_open"  # trial period

@dataclass
class SpendRecord:
    """Spend record for the sliding window."""
    timestamp: datetime
    cost_usd:  float

class ProviderCircuitBreaker:
    """
    Financial circuit breaker for an LLM provider.

    Opens when the consumption rate exceeds N times the historical average.
    Protects against loop bugs and configuration errors that generate
    spend spikes in minutes, not hours.
    """

    def __init__(
        self,
        provider_name: str,
        # Observation window for calculating consumption rate
        window_minutes: int = 10,
        # Multiple of historical average that triggers opening
        spike_multiplier: float = 5.0,
        # Minimum spend to trigger (avoids false positives with low costs)
        min_spend_to_open_usd: float = 1.0,
        # Wait time before transitioning to HALF_OPEN
        open_timeout_seconds: int = 300,  # 5 minutes
    ):
        self.provider_name        = provider_name
        self.window_minutes       = window_minutes
        self.spike_multiplier     = spike_multiplier
        self.min_spend_to_open    = min_spend_to_open_usd
        self.open_timeout         = open_timeout_seconds

        self._state               = CircuitState.CLOSED
        self._spend_window: deque = deque()  # records in the window
        self._historical_rate     = 0.0  # USD/minute historical average
        self._opened_at: datetime | None = None
        self._lock                = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Returns current state, transitioning to HALF_OPEN if appropriate."""
        with self._lock:
            if (self._state == CircuitState.OPEN
                    and self._opened_at is not None
                    and (datetime.utcnow() - self._opened_at).seconds >= self.open_timeout):
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker %s → HALF_OPEN", self.provider_name)
            return self._state

    def allow_request(self) -> bool:
        """
        Should this request be allowed?
        CLOSED and HALF_OPEN allow; OPEN rejects.
        """
        state = self.state
        if state == CircuitState.OPEN:
            logger.warning("Circuit breaker OPEN: rejecting request to %s",
                           self.provider_name)
            return False
        return True

    def record_success(self, cost_usd: float):
        """
        Records a successful call and checks for a spike.
        Must be called AFTER each LLM call to update the window.
        """
        with self._lock:
            now = datetime.utcnow()

            # Add to sliding window
            self._spend_window.append(SpendRecord(timestamp=now, cost_usd=cost_usd))

            # Clean records outside the window
            cutoff = now - timedelta(minutes=self.window_minutes)
            while self._spend_window and self._spend_window[0].timestamp < cutoff:
                self._spend_window.popleft()

            # Calculate current rate (USD/minute in the window)
            window_spend = sum(r.cost_usd for r in self._spend_window)
            current_rate = window_spend / self.window_minutes

            # If we were in HALF_OPEN and cost is normal, close
            if self._state == CircuitState.HALF_OPEN:
                if current_rate <= self._historical_rate * self.spike_multiplier:
                    self._state = CircuitState.CLOSED
                    logger.info("Circuit breaker %s → CLOSED (recovered)",
                                self.provider_name)
                else:
                    self._state = CircuitState.OPEN
                    self._opened_at = now
                    return

            # Update historical average (smoothed exponential moving average)
            if self._historical_rate == 0:
                self._historical_rate = current_rate
            else:
                alpha = 0.1  # smoothing factor: 10% new observation
                self._historical_rate = (
                    alpha * current_rate
                    + (1 - alpha) * self._historical_rate
                )

            # Check for spike
            if (current_rate > self._historical_rate * self.spike_multiplier
                    and window_spend >= self.min_spend_to_open):
                self._state     = CircuitState.OPEN
                self._opened_at = now
                logger.error(
                    "Circuit breaker %s OPENED: current rate=$%.4f/min, "
                    "historical average=$%.4f/min, factor=%.1fx",
                    self.provider_name, current_rate,
                    self._historical_rate, self.spike_multiplier,
                )

    def record_failure(self):
        """Records a provider failure (for metrics, does not affect financial state)."""
        logger.warning("Failure recorded for %s", self.provider_name)
