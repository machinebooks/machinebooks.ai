# Extraído de: LibroCyberrange/cap-02-ciberejercicios.md
# Ejemplo didáctico: configuración de puntuación por tipo de ejercicio
# Fichero: patrones/scoring/exercise_scoring.py

from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class ExerciseType(str, Enum):
    TABLETOP = "tabletop"
    LIVE_FIRE = "live_fire"
    HYBRID = "hybrid"
    PURPLE_TEAM = "purple_team"

class ScoringModel(str, Enum):
    SIMPLE = "simple"           # Puntos por flag capturada
    WEIGHTED = "weighted"       # Puntos ponderados por categoría
    COMPETITIVE = "competitive" # Ranking entre equipos con first-blood

class ScoringCategory(BaseModel):
    name: str
    weight: float                            # Peso en el modelo ponderado
    flags: List[str] = []                    # Flags automáticas
    manual_evaluation: bool = False          # Requiere evaluación del facilitador
    mitre_techniques: List[str] = []         # Técnicas MITRE asociadas

class ExerciseScoringConfig(BaseModel):
    exercise_type: ExerciseType
    scoring_model: ScoringModel
    categories: List[ScoringCategory]

    # Bonificaciones competitivas (solo para live_fire y hybrid)
    first_blood_bonus: int = 50              # Puntos extra por primera captura
    hint_penalty_percent: float = 0.25       # Penalización del 25% por usar pista
    time_bonus_enabled: bool = True          # Bonus por rapidez

    # Umbrales de rendimiento (NIST SP 800-84: objetivos medibles)
    passing_threshold_percent: float = 60.0  # Mínimo para "cumple expectativas"
    excellent_threshold_percent: float = 85.0


# Configuraciones predefinidas para cada tipo de ejercicio
SCORING_PRESETS: Dict[ExerciseType, ExerciseScoringConfig] = {
    ExerciseType.LIVE_FIRE: ExerciseScoringConfig(
        exercise_type=ExerciseType.LIVE_FIRE,
        scoring_model=ScoringModel.COMPETITIVE,
        categories=[
            ScoringCategory(
                name="detection",
                weight=0.30,
                flags=["lateral_movement_detected", "exfiltration_detected"],
                mitre_techniques=["T1021", "T1048"]
            ),
            ScoringCategory(
                name="response",
                weight=0.35,
                flags=["host_isolated", "malware_contained", "ioc_shared"],
                mitre_techniques=["T1486"]  # Data Encrypted for Impact
            ),
            ScoringCategory(
                name="forensics",
                weight=0.35,
                flags=["attack_timeline_complete", "root_cause_identified"],
            ),
        ],
        first_blood_bonus=50,
        hint_penalty_percent=0.25,
    ),
    ExerciseType.PURPLE_TEAM: ExerciseScoringConfig(
        exercise_type=ExerciseType.PURPLE_TEAM,
        scoring_model=ScoringModel.SIMPLE,
        categories=[
            ScoringCategory(
                name="technique_coverage",
                weight=0.50,
                mitre_techniques=["T1558.003", "T1558.004", "T1003.001"],
            ),
            ScoringCategory(
                name="detection_rule_created",
                weight=0.30,
                manual_evaluation=True,
            ),
            ScoringCategory(
                name="documentation",
                weight=0.20,
                manual_evaluation=True,
            ),
        ],
        first_blood_bonus=0,          # No aplica en colaborativo
        hint_penalty_percent=0.0,     # Sin penalización: el objetivo es aprender
    ),
}
