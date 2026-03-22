# Extraído de: LibroCyberrange/cap-16-ia-por-que.md
# Ejemplo didáctico: patrones/ia/cost_estimator.py

EXERCISE_PROFILES = {
    "basic_ctf": {
        # CTF individual, 2 horas, 10 retos
        "scenario_generation": {
            "calls": 1, "model": "sonnet",
            "avg_input_tokens": 2000, "avg_output_tokens": 4000
        },
        "coaching_hints": {
            "calls": 30, "model": "haiku",  # ~3 pistas por reto
            "avg_input_tokens": 500, "avg_output_tokens": 200
        },
        "evaluation": {
            "calls": 1, "model": "sonnet",
            "avg_input_tokens": 3000, "avg_output_tokens": 2000
        },
        "estimated_cost_usd": 0.12,  # ~0,12 USD por ejercicio
    },
    "team_exercise_medium": {
        # 4 equipos, 4 horas, escenario AD completo
        "scenario_generation": {
            "calls": 1, "model": "sonnet",
            "avg_input_tokens": 5000, "avg_output_tokens": 8000
        },
        "coaching_hints": {
            "calls": 200, "model": "haiku",  # ~50 por equipo
            "avg_input_tokens": 800, "avg_output_tokens": 300
        },
        "red_team_planning": {
            "calls": 5, "model": "sonnet",
            "avg_input_tokens": 3000, "avg_output_tokens": 4000
        },
        "evaluation": {
            "calls": 4, "model": "sonnet",  # 1 por equipo
            "avg_input_tokens": 5000, "avg_output_tokens": 3000
        },
        "estimated_cost_usd": 0.85,  # ~0,85 USD por ejercicio
    },
    "enterprise_locked_shields": {
        # 8 equipos, 2 días, escenario multi-segmento complejo
        "scenario_generation": {
            "calls": 3, "model": "opus",  # Escenario complejo
            "avg_input_tokens": 8000, "avg_output_tokens": 12000
        },
        "coaching_hints": {
            "calls": 1500, "model": "haiku",
            "avg_input_tokens": 1000, "avg_output_tokens": 400
        },
        "red_team_planning": {
            "calls": 20, "model": "sonnet",
            "avg_input_tokens": 5000, "avg_output_tokens": 6000
        },
        "blue_team_assist": {
            "calls": 200, "model": "haiku",
            "avg_input_tokens": 800, "avg_output_tokens": 300
        },
        "evaluation": {
            "calls": 8, "model": "sonnet",
            "avg_input_tokens": 8000, "avg_output_tokens": 5000
        },
        "report_generation": {
            "calls": 1, "model": "sonnet",
            "avg_input_tokens": 10000, "avg_output_tokens": 6000
        },
        "estimated_cost_usd": 8.50,  # ~8,50 USD por ejercicio
    },
}

def estimate_exercise_cost(profile: str) -> dict:
    """Estima el coste de IA de un ejercicio antes de ejecutarlo."""
    p = EXERCISE_PROFILES[profile]
    breakdown = {}
    total = 0.0

    for task_name, task in p.items():
        if task_name == "estimated_cost_usd":
            continue
        model_prices = CyberRangeAIService.PRICING[
            AIModel(f"claude-{task['model']}-4-6"
                    if task['model'] != 'haiku'
                    else "claude-haiku-4-5")
        ]
        cost = task["calls"] * (
            task["avg_input_tokens"] * model_prices["input"] / 1_000_000 +
            task["avg_output_tokens"] * model_prices["output"] / 1_000_000
        )
        breakdown[task_name] = round(cost, 4)
        total += cost

    return {
        "profile": profile,
        "breakdown": breakdown,
        "total_estimated_usd": round(total, 2)
    }
