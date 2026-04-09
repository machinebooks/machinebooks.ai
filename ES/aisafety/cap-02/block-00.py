# Extraido de: LibroAISafety/cap-02-model-cards.md
# Clasificación de evaluaciones de una Model Card
# Ejecutar tras extraer las secciones de benchmarks

BENCHMARKS_CAPACIDAD = {
    "MMLU", "MMLU-Pro", "HumanEval", "SWE-bench",
    "GPQA", "MATH-500", "ARC-AGI", "τ2-bench",
    "WebArena", "OSWorld", "HellaSwag", "Winogrande"
}

EVALUACIONES_SEGURIDAD = {
    "CBRN", "CyberGym", "StrongREJECT", "persuasion",
    "autonomy", "self-replication", "tool-misuse",
    "prompt-injection", "jailbreak-resistance"
}

def auditar_model_card(evaluaciones_listadas: list[str]) -> dict:
    """Clasifica las evaluaciones de una Model Card en
    capacidad vs. seguridad, e identifica gaps."""
    capacidad = [e for e in evaluaciones_listadas
                 if e in BENCHMARKS_CAPACIDAD]
    seguridad = [e for e in evaluaciones_listadas
                 if e in EVALUACIONES_SEGURIDAD]
    desconocidas = [e for e in evaluaciones_listadas
                    if e not in BENCHMARKS_CAPACIDAD
                    and e not in EVALUACIONES_SEGURIDAD]

    # Gaps: evaluaciones estándar que no aparecen
    gaps_capacidad = BENCHMARKS_CAPACIDAD - set(capacidad)
    gaps_seguridad = EVALUACIONES_SEGURIDAD - set(seguridad)

    return {
        "capacidad": capacidad,
        "seguridad": seguridad,
        "desconocidas": desconocidas,
        "gaps_capacidad": gaps_capacidad,
        "gaps_seguridad": gaps_seguridad,
        "ratio_seguridad": len(seguridad) / max(len(evaluaciones_listadas), 1)
    }
