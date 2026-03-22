# Extraído de: LibroCyberrange/cap-28-futuro-agentes-ia.md
# Ciclo de entrenamiento continuo del Cyber Range autónomo
# Ejemplo didáctico: orchestration/continuous_training.py

from agents import Agent, Runner, function_tool
from datetime import datetime, timedelta

@function_tool
def check_training_schedule(organization_id: str) -> dict:
    """Verifica qué participantes necesitan entrenamiento."""
    return {
        "participants_due": [
            {
                "id": "analyst_042",
                "role": "soc_tier1",
                "last_training": "2026-03-14",
                "weak_areas": ["T1055", "T1218"],
                "required_by_compliance": "NIS-2",
                "deadline": "2026-04-01",
            },
        ],
        "models_due_for_retraining": [
            {
                "model": "alert_classifier_v3",
                "accuracy_current": 0.91,
                "accuracy_target": 0.95,
                "data_needed": "500_labeled_incidents",
            },
        ],
    }

@function_tool
def generate_and_deploy_scenario(spec: dict) -> dict:
    """Genera, valida y despliega un escenario completo."""
    return {
        "scenario_id": "auto_2026_0321_001",
        "status": "deployed",
        "estimated_duration_minutes": 90,
        "techniques_covered": ["T1055.012", "T1218.011"],
        "data_generation_enabled": True,  # Dual training activo
    }

@function_tool
def evaluate_session(scenario_id: str, participant_id: str) -> dict:
    """Evalúa el rendimiento post-ejercicio."""
    return {
        "score": 72,
        "techniques_mastered": ["T1218.011"],
        "techniques_still_weak": ["T1055.012"],
        "recommendation": "Repetir T1055 con evasion_level 2",
        "labeled_data_generated": 1247,  # Eventos etiquetados
        "model_training_data_saved": True,
    }

continuous_training_orchestrator = Agent(
    name="continuous_training",
    model="claude-sonnet-4-6",
    instructions="""Eres el orquestador de entrenamiento continuo del
    Cyber Range. Tu ciclo de operación es:

    1. Cada día, verifica qué participantes necesitan entrenamiento
       (por competencias débiles, por requisitos de compliance,
       o por caducidad del último ejercicio)
    2. Genera escenarios personalizados para cada participante
    3. Despliega los escenarios en las workzones disponibles
    4. Monitoriza las sesiones y ajusta dificultad en tiempo real
    5. Evalúa el rendimiento y actualiza los perfiles
    6. Recopila datos etiquetados para reentrenamiento de modelos
    7. Genera informes de compliance para auditores

    Prioriza participantes con requisitos regulatorios (NIS-2, DORA)
    sobre entrenamiento opcional.""",
    tools=[
        check_training_schedule,
        generate_and_deploy_scenario,
        evaluate_session,
    ],
)
