# Extraído de: LibroCyberrange/cap-04-claude-ecosistema.md
# Asignación de modelos configurable desde base de datos
# Ejemplo didáctico: patrones/config/model_registry.py

from dataclasses import dataclass
from enum import Enum

class ModelTier(str, Enum):
    OPUS = "claude-opus-4-6"       # Máxima capacidad
    SONNET = "claude-sonnet-4-6"   # Estándar
    HAIKU = "claude-haiku-4-5"     # Velocidad/coste

# Configuración por servicio — se carga de BD, no hardcodeada
DEFAULT_MODEL_ASSIGNMENTS = {
    "scenario_generator_complex": ModelTier.OPUS,
    "scenario_generator_standard": ModelTier.SONNET,
    "ansible_playbook_generator": ModelTier.SONNET,
    "adaptive_coach": ModelTier.HAIKU,
    "post_exercise_evaluator": ModelTier.OPUS,
    "action_classifier": ModelTier.HAIKU,
    "threat_analyzer": ModelTier.SONNET,
    "report_generator": ModelTier.SONNET,
    "red_team_agent": ModelTier.SONNET,
    "flag_hint_generator": ModelTier.HAIKU,
}

@dataclass
class ModelConfig:
    """Configuración de modelo para un servicio de IA."""
    service_name: str
    model: str
    max_tokens: int
    temperature: float
    timeout_seconds: int

    @classmethod
    def from_db(cls, service_name: str) -> "ModelConfig":
        """Carga la configuración desde base de datos.
        Si no existe, usa el valor por defecto."""
        db_config = AIServiceConfig.query.filter_by(
            service_name=service_name,
            is_active=True
        ).first()

        if db_config:
            return cls(
                service_name=service_name,
                model=db_config.model_name,
                max_tokens=db_config.max_tokens,
                temperature=db_config.temperature,
                timeout_seconds=db_config.timeout_seconds
            )

        # Fallback a configuración por defecto
        default_model = DEFAULT_MODEL_ASSIGNMENTS.get(
            service_name, ModelTier.SONNET
        )
        return cls(
            service_name=service_name,
            model=default_model,
            max_tokens=4096,
            temperature=0.3,
            timeout_seconds=60
        )
