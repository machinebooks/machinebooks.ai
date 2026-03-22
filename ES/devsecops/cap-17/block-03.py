# Extraído de: LibroDevSecOps/cap-17-aiact-pipeline.md
from dataclasses import dataclass, field

@dataclass
class ComplianceCheck:
    article: str
    requirement: str
    check_type: str        # "automated" | "agent" | "manual"
    status: str = "pending"  # "passed" | "failed" | "warning" | "pending"
    evidence: str = ""
    details: str = ""

def build_high_risk_checklist(pipeline_artifacts: dict) -> list[ComplianceCheck]:
    """Genera checklist para sistema de alto riesgo basándose en artefactos del pipeline."""
    checks = []

    # Art. 9 — Sistema de gestión de riesgos
    checks.append(ComplianceCheck(
        article="Art. 9",
        requirement="Documentación de riesgos identificados y medidas de mitigación",
        check_type="agent",
        status="passed" if pipeline_artifacts.get("risk_assessment") else "failed",
        evidence=pipeline_artifacts.get("risk_assessment_path", "")
    ))

    # Art. 10 — Datos y gobernanza de datos
    checks.append(ComplianceCheck(
        article="Art. 10",
        requirement="Documentación de datos de entrenamiento/validación/test",
        check_type="automated",
        status="passed" if pipeline_artifacts.get("data_card") else "failed",
        evidence=pipeline_artifacts.get("data_card_path", "")
    ))

    # Art. 11 — Documentación técnica
    checks.append(ComplianceCheck(
        article="Art. 11",
        requirement="Documentación técnica completa según Anexo IV",
        check_type="agent",
        status="passed" if pipeline_artifacts.get("technical_doc") else "failed",
        evidence=pipeline_artifacts.get("technical_doc_path", "")
    ))

    # Art. 12 — Registro de eventos (logging)
    has_logging = pipeline_artifacts.get("llm_usage_logs", False)
    checks.append(ComplianceCheck(
        article="Art. 12",
        requirement="Logging automático de operaciones del sistema IA",
        check_type="automated",
        status="passed" if has_logging else "failed",
        evidence="LLM usage logs activos" if has_logging else "Sin logging detectado"
    ))

    # Art. 13 — Transparencia
    checks.append(ComplianceCheck(
        article="Art. 13",
        requirement="Instrucciones de uso para deployers con información suficiente",
        check_type="agent",
        status="pending",  # Requiere evaluación cualitativa
        evidence=pipeline_artifacts.get("user_instructions_path", "")
    ))

    # Art. 14 — Supervisión humana
    autonomy = pipeline_artifacts.get("autonomy_level", "autonomous")
    checks.append(ComplianceCheck(
        article="Art. 14",
        requirement="Mecanismo de supervisión humana implementado",
        check_type="automated",
        status="passed" if autonomy != "autonomous" else "failed",
        evidence=f"Nivel de autonomía: {autonomy}"
    ))

    # Art. 15 — Exactitud, solidez y ciberseguridad
    has_security_scan = pipeline_artifacts.get("sast_results") is not None
    has_sca = pipeline_artifacts.get("sbom") is not None
    checks.append(ComplianceCheck(
        article="Art. 15 (ciberseguridad)",
        requirement="Escaneo de seguridad del código y dependencias",
        check_type="automated",
        status="passed" if (has_security_scan and has_sca) else "failed",
        evidence=f"SAST: {'sí' if has_security_scan else 'no'}, SCA/SBOM: {'sí' if has_sca else 'no'}"
    ))

    # Art. 15 — Resiliencia adversarial
    has_prompt_injection_test = pipeline_artifacts.get("prompt_injection_results")
    checks.append(ComplianceCheck(
        article="Art. 15 (resiliencia)",
        requirement="Testing adversarial contra prompt injection",
        check_type="automated",
        status="passed" if has_prompt_injection_test else "warning",
        evidence=pipeline_artifacts.get("prompt_injection_summary", "Sin tests adversariales")
    ))

    return checks
