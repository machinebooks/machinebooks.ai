# Extraido de: LibroAISafety/cap-10-governance-operativa.md
# ai_policy_engine.py — Motor de políticas para sistemas de IA
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

class PolicyResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"

@dataclass
class PolicyRule:
    """Una regla de política verificable automáticamente."""
    rule_id: str
    description: str
    severity: str          # "blocking", "warning"
    check: Callable        # Función que evalúa la regla
    remediation: str       # Qué hacer si no se cumple

@dataclass
class PolicyEvaluation:
    """Resultado de evaluar todas las políticas de un sistema."""
    system_name: str
    timestamp: datetime
    results: list[dict]
    deployable: bool       # True si no hay reglas blocking en FAIL

def create_ai_policy_rules() -> list[PolicyRule]:
    """
    Define las reglas de política como código.
    Cada regla es una función que evalúa un sistema.
    """
    rules = [
        PolicyRule(
            rule_id="POL-001",
            description="Sistema debe tener clasificación de riesgo asignada",
            severity="blocking",
            check=lambda s: PolicyResult.PASS 
                if s.get("risk_tier") 
                else PolicyResult.FAIL,
            remediation="Ejecutar classify_ai_act_risk() y asignar tier"
        ),
        PolicyRule(
            rule_id="POL-002",
            description="Evaluación de seguridad vigente según tier",
            severity="blocking",
            check=lambda s: _check_eval_currency(s),
            remediation="Ejecutar evaluación de seguridad actualizada"
        ),
        PolicyRule(
            rule_id="POL-003",
            description="Guardrails de output activos para Tier 2+",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("risk_tier") == "tier_1"
                or s.get("output_guardrails_active", False)
                else PolicyResult.FAIL,
            remediation="Activar guardrails de output antes de despliegue"
        ),
        PolicyRule(
            rule_id="POL-004",
            description="Ficha de transparencia completada",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("transparency_card_complete", False)
                else PolicyResult.FAIL,
            remediation="Completar AISystemCard (ver Capítulo 8)"
        ),
        PolicyRule(
            rule_id="POL-005",
            description="Human-in-the-loop para Tier 3",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("risk_tier") != "tier_3"
                or s.get("human_in_the_loop", False)
                else PolicyResult.FAIL,
            remediation="Implementar mecanismo de supervisión humana"
        ),
        PolicyRule(
            rule_id="POL-006",
            description="Modelo del proveedor aprobado",
            severity="blocking",
            check=lambda s: PolicyResult.PASS
                if s.get("model_name") in APPROVED_MODELS
                else PolicyResult.FAIL,
            remediation="Solicitar aprobación del modelo al comité"
        ),
        PolicyRule(
            rule_id="POL-007",
            description="Logging de interacciones activo",
            severity="warning",
            check=lambda s: PolicyResult.PASS
                if s.get("interaction_logging", False)
                else PolicyResult.WARN,
            remediation="Configurar logging sin captura de PII"
        ),
    ]
    return rules

APPROVED_MODELS = [
    "claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-6",
    "gpt-4o", "gpt-4o-mini",
    "gemini-2.0-flash", "gemini-2.0-pro",
]

def _check_eval_currency(system: dict) -> PolicyResult:
    """Verifica que la evaluación de seguridad está vigente."""
    last_eval = system.get("last_security_eval")
    if not last_eval:
        return PolicyResult.FAIL
    
    max_days = {"tier_1": 90, "tier_2": 30, "tier_3": 7}
    tier = system.get("risk_tier", "tier_1")
    age = (datetime.utcnow() - last_eval).days
    
    if age > max_days.get(tier, 90):
        return PolicyResult.FAIL
    return PolicyResult.PASS

def evaluate_system(
    system: dict, 
    rules: list[PolicyRule]
) -> PolicyEvaluation:
    """Evalúa un sistema contra todas las reglas de política."""
    results = []
    for rule in rules:
        result = rule.check(system)
        results.append({
            "rule_id": rule.rule_id,
            "description": rule.description,
            "result": result.value,
            "severity": rule.severity,
            "remediation": rule.remediation 
                if result == PolicyResult.FAIL 
                else None
        })
    
    # Deployable = no hay reglas blocking en FAIL
    blocking_fails = [
        r for r in results 
        if r["severity"] == "blocking" 
        and r["result"] == "fail"
    ]
    
    return PolicyEvaluation(
        system_name=system.get("name", "unknown"),
        timestamp=datetime.utcnow(),
        results=results,
        deployable=len(blocking_fails) == 0
    )
