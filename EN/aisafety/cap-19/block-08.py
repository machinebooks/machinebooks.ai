# Extracted from: LibroAISafety/ch-19-observability.md
import math
from collections import deque

class AnomalyDetector:
    """Anomaly detection with EWMA for security metrics."""

    def __init__(self, alpha: float = 0.1, threshold_sigma: float = 3.0):
        self._alpha = alpha  # Smoothing factor (0.1 = low memory)
        self._threshold = threshold_sigma
        self._ewma: float = 0.0
        self._ewma_var: float = 0.0
        self._initialized = False
        self._window: deque[float] = deque(maxlen=1000)

    def observe(self, value: float) -> dict:
        """Records a value and returns whether it is anomalous."""
        if not self._initialized:
            self._ewma = value
            self._ewma_var = 0.0
            self._initialized = True
            return {"anomaly": False, "z_score": 0.0}

        # Update EWMA
        diff = value - self._ewma
        self._ewma += self._alpha * diff
        self._ewma_var = (1 - self._alpha) * (
            self._ewma_var + self._alpha * diff * diff
        )
        std = math.sqrt(self._ewma_var) if self._ewma_var > 0 else 1.0
        z_score = abs(diff) / std if std > 0 else 0.0

        self._window.append(value)

        return {
            "anomaly": z_score > self._threshold,
            "z_score": round(z_score, 2),
            "ewma": round(self._ewma, 2),
            "std": round(std, 2),
            "value": value,
        }
