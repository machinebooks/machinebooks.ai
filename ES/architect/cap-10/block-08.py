# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/bots/pricing_bot.py

import time
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class UploadResult:
    """Resultado de una operación de carga masiva."""
    total_rows: int = 0
    successful: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return self.successful / self.total_rows

class PricingBot(BaseBot):
    """Bot de automatización para el configurador de precios corporativo."""

    REQUIRED_COLUMNS = {"codigo_servicio", "precio_base", "descuento_maximo", "vigencia"}
    MAX_BATCH_SIZE = 50  # Procesar en lotes para evitar timeouts del sistema externo

