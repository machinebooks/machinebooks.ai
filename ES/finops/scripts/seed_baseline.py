# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# scripts/seed_baseline.py — Semilla inicial de configuración HumanBaseline
# Valores basados en observación directa y entrevistas con el equipo.
# Revisión programada: trimestral.

INITIAL_BASELINES = [
    {
        "task_type": "offer_generation",
        "role": "senior_consultant",
        "human_minutes": 120.0,          # rango observado: 90-150 min
        "hourly_cost_eur": 55.0,
        "supervision_overhead": 0.10,
        "productivity_capture": 0.70,
        "is_bottleneck": True,           # limita la capacidad comercial
        "acceptance_rate": 0.88,
        "notes": "Validado con muestra de 50 ofertas. Revisar Q2.",
    },
    {
        "task_type": "technical_analysis",
        "role": "senior_consultant",
        "human_minutes": 90.0,
        "hourly_cost_eur": 55.0,
        "supervision_overhead": 0.15,    # más supervisión: análisis crítico
        "productivity_capture": 0.65,
        "is_bottleneck": False,
        "acceptance_rate": 0.82,
        "notes": "Alta varianza según complejidad del cliente.",
    },
    {
        "task_type": "compliance_report",
        "role": "compliance_officer",
        "human_minutes": 180.0,
        "hourly_cost_eur": 48.0,
        "supervision_overhead": 0.20,    # supervisión alta: documento regulatorio
        "productivity_capture": 0.60,
        "is_bottleneck": True,
        "acceptance_rate": 0.75,
        "notes": "Ahorro mayor pero supervisión más intensiva.",
    },
    {
        "task_type": "email_courtesy",
        "role": "junior_consultant",
        "human_minutes": 5.0,
        "hourly_cost_eur": 28.0,
        "supervision_overhead": 0.30,
        "productivity_capture": 0.40,
        "is_bottleneck": False,
        "acceptance_rate": 0.45,         # baja: calidad mediocre observada
        "notes": "ROI negativo confirmado. Mantener solo para análisis.",
        "active": False,                 # desactivado del cálculo de ROI
    },
]
