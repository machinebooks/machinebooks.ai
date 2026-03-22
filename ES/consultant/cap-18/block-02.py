# Extraído de: LibroConsultor/cap-18-onboarding.md
from dataclasses import dataclass
from typing import Optional

@dataclass
class Scenario:
    """Escenario de práctica para onboarding."""
    scenario_id: str
    title: str
    difficulty: int                  # 1-5
    category: str                    # "analysis", "delivery", "client", "estimation"
    context: str                     # Situación que el junior debe resolver
    materials: list[str]             # Documentos adjuntos (fragmentos de pliego, etc.)
    task: str                        # Lo que se pide al junior
    evaluation_criteria: list[dict]  # Criterios con peso para evaluar
    max_time_minutes: int = 60
    reference_solution: str = ""     # Solución de referencia (no se muestra al junior)
    common_mistakes: list[str] = None  # Errores frecuentes a detectar

SCENARIOS_LIBRARY = [
    Scenario(
        scenario_id="SCN-001",
        title="Análisis de requisitos de un pliego público",
        difficulty=1,
        category="analysis",
        context="""Un organismo público ha publicado un pliego para auditoría
        de seguridad. Tu responsable te pide que extraigas los requisitos
        obligatorios de solvencia técnica y los criterios de valoración
        con sus ponderaciones. Tienes el fragmento relevante del pliego.""",
        materials=["pliego_simulado_fragmento_01.md"],
        task="""Produce una tabla con: (1) requisitos obligatorios de solvencia,
        (2) criterios de valoración con ponderación, (3) plazos clave.
        Incluye una recomendación go/no-go con justificación.""",
        evaluation_criteria=[
            {"criterion": "Completitud de requisitos extraídos", "weight": 0.3},
            {"criterion": "Corrección de ponderaciones", "weight": 0.2},
            {"criterion": "Identificación de plazos críticos", "weight": 0.2},
            {"criterion": "Calidad de la recomendación go/no-go", "weight": 0.3},
        ],
        max_time_minutes=45,
        common_mistakes=[
            "Confundir requisitos obligatorios con criterios de valoración",
            "No detectar plazos implícitos (como plazo de subsanación)",
            "Dar recomendación sin considerar la capacidad real del equipo"
        ]
    ),
    Scenario(
        scenario_id="SCN-005",
        title="Gestión de hallazgo crítico con el cliente",
        difficulty=3,
        category="client",
        context="""Durante una auditoría de seguridad encuentras que el sistema
        del cliente tiene una vulnerabilidad crítica en el módulo de
        autenticación. El CISO del cliente te dice informalmente que
        'ya lo saben pero no tienen presupuesto para corregirlo este año'.
        Tu responsable de proyecto no está disponible hasta mañana.""",
        materials=[],
        task="""Describe: (1) qué haces en las próximas 2 horas,
        (2) cómo lo documentas, (3) qué le dices al CISO,
        (4) qué le dices a tu responsable mañana. Justifica cada decisión.""",
        evaluation_criteria=[
            {"criterion": "Protocolo de escalado correcto", "weight": 0.3},
            {"criterion": "Documentación adecuada del hallazgo", "weight": 0.2},
            {"criterion": "Comunicación profesional con el CISO", "weight": 0.25},
            {"criterion": "Gestión del riesgo propio y del cliente", "weight": 0.25},
        ],
        max_time_minutes=30,
        common_mistakes=[
            "Esperar a mañana sin hacer nada",
            "Enviar un email formal al CISO sin hablar antes con su responsable",
            "No documentar la conversación informal como evidencia",
            "Minimizar el hallazgo porque 'el cliente ya lo sabe'"
        ]
    )
]
