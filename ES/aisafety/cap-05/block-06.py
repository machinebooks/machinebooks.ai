# Extraido de: LibroAISafety/cap-05-system-prompt.md
# Framework mínimo de testing para system prompts
from dataclasses import dataclass
from typing import Literal

@dataclass
class PromptTestCase:
    """Caso de test para un system prompt."""
    test_id: str
    category: Literal[
        "regression", "adversarial", "compatibility"
    ]
    user_input: str
    expected_behavior: Literal[
        "should_answer", "should_refuse", "should_not_leak"
    ]
    description: str

def run_prompt_test_suite(
    prompt: str,
    model: str,
    tests: list[PromptTestCase],
) -> dict:
    """
    Ejecuta la suite de tests contra un prompt y modelo.
    Retorna resultados con tasa de acierto por categoría.
    """
    results = {"passed": 0, "failed": 0, "by_category": {}}
    for test in tests:
        # Ejecutar el test contra la API (simplificado)
        response = call_model(model, prompt, test.user_input)
        passed = evaluate_response(
            response, test.expected_behavior
        )
        cat = test.category
        if cat not in results["by_category"]:
            results["by_category"][cat] = {"passed": 0, "total": 0}
        results["by_category"][cat]["total"] += 1
        if passed:
            results["passed"] += 1
            results["by_category"][cat]["passed"] += 1
        else:
            results["failed"] += 1
    return results
