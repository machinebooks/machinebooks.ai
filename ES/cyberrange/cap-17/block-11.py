# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/generation_metrics.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GenerationMetrics:
    """Métricas de una generación de escenario con IA."""

    # Identificación
    template_id: int
    agent_model: str           # "claude-sonnet-4-6" o "claude-opus-4-6"
    complexity: str            # "standard" o "complex"

    # Rendimiento
    generation_time_seconds: float    # Tiempo total de generación
    tool_calls_count: int             # Número de llamadas a herramientas
    validation_passed: bool           # Si pasó validación a la primera

    # Tokens y coste
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float

    # Calidad
    validation_errors: int
    validation_warnings: int
    human_review_required: bool
    human_approved: bool = False

    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
