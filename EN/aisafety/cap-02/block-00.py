# Extracted from: LibroAISafety/ch-02-model-cards.md
# Classification of evaluations from a Model Card
# Execute after extracting the benchmark sections

CAPABILITY_BENCHMARKS = {
    "MMLU", "MMLU-Pro", "HumanEval", "SWE-bench",
    "GPQA", "MATH-500", "ARC-AGI", "τ2-bench",
    "WebArena", "OSWorld", "HellaSwag", "Winogrande"
}

SAFETY_EVALUATIONS = {
    "CBRN", "CyberGym", "StrongREJECT", "persuasion",
    "autonomy", "self-replication", "tool-misuse",
    "prompt-injection", "jailbreak-resistance"
}

def audit_model_card(listed_evaluations: list[str]) -> dict:
    """Classifies evaluations from a Model Card into
    capability vs. safety, and identifies gaps."""
    capability = [e for e in listed_evaluations
                  if e in CAPABILITY_BENCHMARKS]
    safety = [e for e in listed_evaluations
              if e in SAFETY_EVALUATIONS]
    unknown = [e for e in listed_evaluations
               if e not in CAPABILITY_BENCHMARKS
               and e not in SAFETY_EVALUATIONS]

    # Gaps: standard evaluations that do not appear
    capability_gaps = CAPABILITY_BENCHMARKS - set(capability)
    safety_gaps = SAFETY_EVALUATIONS - set(safety)

    return {
        "capability": capability,
        "safety": safety,
        "unknown": unknown,
        "capability_gaps": capability_gaps,
        "safety_gaps": safety_gaps,
        "safety_ratio": len(safety) / max(len(listed_evaluations), 1)
    }
