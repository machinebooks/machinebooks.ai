# Extraído de: LibroDevSecOps/cap-17-aiact-pipeline.md
# Mapeo ISO 42001 <-> AI Act <-> Artefacto del pipeline
ISO_AIACT_MAPPING = [
    {
        "iso_control": "A.6.2.2",
        "iso_description": "AI risk assessment",
        "aiact_article": "Art. 9",
        "aiact_requirement": "Sistema de gestión de riesgos",
        "pipeline_evidence": "risk_assessment.json",
        "verification": "automated"
    },
    {
        "iso_control": "A.7.2",
        "iso_description": "Data for AI systems",
        "aiact_article": "Art. 10",
        "aiact_requirement": "Datos y gobernanza de datos",
        "pipeline_evidence": "data_card.yaml",
        "verification": "agent"
    },
    {
        "iso_control": "A.6.2.4",
        "iso_description": "Documentation of AI system",
        "aiact_article": "Art. 11 + Anexo IV",
        "aiact_requirement": "Documentación técnica",
        "pipeline_evidence": "ai-act-technical-doc.md",
        "verification": "agent"
    },
    {
        "iso_control": "A.8.2",
        "iso_description": "Logging of AI system operation",
        "aiact_article": "Art. 12",
        "aiact_requirement": "Registro de eventos",
        "pipeline_evidence": "llm_usage_logs/",
        "verification": "automated"
    },
    {
        "iso_control": "A.8.4",
        "iso_description": "Human oversight of AI systems",
        "aiact_article": "Art. 14",
        "aiact_requirement": "Supervisión humana",
        "pipeline_evidence": "autonomy_level in manifest",
        "verification": "automated"
    },
    {
        "iso_control": "A.6.2.6",
        "iso_description": "AI system security",
        "aiact_article": "Art. 15",
        "aiact_requirement": "Ciberseguridad",
        "pipeline_evidence": "sast_results.json + sbom.json + prompt_injection_results.json",
        "verification": "automated"
    },
]

def verify_iso_mapping(
    mapping: list[dict],
    pipeline_artifacts: dict
) -> list[dict]:
    """Verifica cada control ISO 42001 contra artefactos del pipeline."""
    results = []
    for control in mapping:
        evidence_key = control["pipeline_evidence"].split(".")[0]
        has_evidence = pipeline_artifacts.get(evidence_key) is not None

        results.append({
            "iso_control": control["iso_control"],
            "aiact_article": control["aiact_article"],
            "status": "evidencia_disponible" if has_evidence else "evidencia_pendiente",
            "evidence_path": control["pipeline_evidence"],
            "verification_type": control["verification"]
        })

    return results
