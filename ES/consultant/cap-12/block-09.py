# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
def continuous_audit_check(
    framework_key: str,
    docs_repo_url: str,
    previous_results: dict,
    alert_threshold: str = "media"
) -> dict:
    """Ejecuta una verificación de auditoría continua."""
    # Sincronizar documentos desde el repositorio
    current_docs = sync_documents(docs_repo_url)

    # Detectar documentos modificados desde la última auditoría
    changed_docs = detect_changes(current_docs, previous_results)

    if not changed_docs:
        return {"status": "sin_cambios", "changes": []}

    # Re-evaluar solo los controles afectados por documentos modificados
    agent = AuditAgent(framework=framework_key)
    affected_controls = map_docs_to_controls(changed_docs)
    new_findings = []

    for control in affected_controls:
        result = agent.evaluate_control(control)
        prev_status = previous_results.get(control.control_id, {}).get("status")

        if result.status != prev_status:
            new_findings.append({
                "control": control.control_id,
                "previous_status": prev_status,
                "current_status": result.status,
                "change_reason": result.justification
            })

    # Alertar si hay degradaciones
    degradations = [
        f for f in new_findings
        if is_degradation(f["previous_status"], f["current_status"])
    ]

    return {
        "status": "cambios_detectados",
        "documents_changed": len(changed_docs),
        "controls_re_evaluated": len(affected_controls),
        "new_findings": new_findings,
        "degradations": degradations,
        "alert": len(degradations) > 0
    }
