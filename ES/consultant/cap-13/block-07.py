# Extraído de: LibroConsultor/cap-13-gap-analysis.md
def run_gap_analysis(
    evidence_dir: str,
    frameworks: list[str],
    org_profile: str,
    target_level: MaturityLevel = MaturityLevel.GESTIONADO,
) -> dict:
    """Ejecuta un gap analysis completo multi-framework."""
    # 1. Inicializar agente y procesador
    agent = GapAnalysisAgent(org_profile, target_level)
    processor = EvidenceProcessor()

    # 2. Cargar frameworks solicitados
    for fw in frameworks:
        agent.load_framework(f"frameworks/{fw}.yaml")
    agent.load_criteria(f"criteria/{org_profile}.yaml")

    # 3. Procesar toda la documentación del cliente
    for doc_path in Path(evidence_dir).glob("**/*"):
        if doc_path.suffix in (".pdf", ".docx", ".xlsx"):
            processor.process_document(str(doc_path))

    # 4. Ejecutar análisis multi-framework deduplicado
    analyzer = MultiFrameworkAnalyzer(agent)
    gaps = analyzer.run_unified_analysis(processor)

    # 5. Generar roadmap de remediación
    roadmap_gen = RoadmapGenerator()
    roadmap = roadmap_gen.generate(
        gaps,
        start=date.today(),
        available_capacity_days_month=20,
    )

    # 6. Generar resumen ejecutivo con Opus
    executive_summary = generate_executive_summary(
        gaps, roadmap, org_profile
    )

    # 7. Calcular métricas de cumplimiento
    metrics = calculate_compliance_metrics(gaps, frameworks)

    return {
        "gaps": gaps,
        "roadmap": roadmap,
        "executive_summary": executive_summary,
        "metrics": metrics,
        "total_effort_days": sum(g.effort_days for g in gaps),
        "low_confidence_items": [
            g for g in gaps if g.confidence < 0.6
        ],
    }
