# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
async def run_multi_framework_analysis(
    client_id: str,
    project_id: str,
    frameworks: list[str]
) -> dict:
    """Ejecuta análisis de cumplimiento contra múltiples frameworks,
    aprovechando los mapeos entre controles para evitar duplicación."""

    results = {}
    consolidated_controls = set()

    for framework in frameworks:
        sections = get_all_sections(framework)
        agent = create_compliance_agent(client_id, project_id)

        framework_findings = await agent.run(
            f"Ejecuta análisis de cumplimiento completo contra "
            f"'{framework}'. Los controles ya evaluados por "
            f"equivalencia con otro framework son: "
            f"{list(consolidated_controls)}. Para esos controles, "
            f"verifica que la evaluación previa aplica y referénciala "
            f"en lugar de repetir el análisis completo."
        )

        # Actualiza controles consolidados con mapeos
        findings = extract_findings(framework_findings)
        for f in findings:
            mappings = get_framework_mapping(
                framework, f["framework_ref"], "all"
            )
            for m in mappings:
                if m["relationship"] == "EQUIVALENTE":
                    consolidated_controls.add(
                        f"{m['target_framework']}:{m['target_control']}"
                    )

        results[framework] = findings

    return {
        "frameworks_analyzed": frameworks,
        "total_findings": sum(len(f) for f in results.values()),
        "findings_by_framework": {
            k: len(v) for k, v in results.items()
        },
        "controls_consolidated": len(consolidated_controls),
        "results": results
    }
