# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
# Runbook: CVE crítica en dependencia
def runbook_critical_cve(cve_id: str, affected_services: list[str]) -> dict:
    """Ejecuta el runbook para una CVE crítica en dependencia."""
    results = {"steps": []}

    # Paso 1: Verificar qué servicios usan la dependencia vulnerable
    for service in affected_services:
        sbom = query_sbom_for_service(service)
        vuln_deps = [d for d in sbom if d.get("cve") == cve_id]
        results["steps"].append({
            "step": "inventory",
            "service": service,
            "vulnerable_dependencies": vuln_deps,
            "status": "vulnerable" if vuln_deps else "clean"
        })

    # Paso 2: Evaluar si existe parche disponible
    patch_info = check_patch_availability(cve_id)
    results["steps"].append({
        "step": "patch_check",
        "cve": cve_id,
        "patch_available": patch_info["available"],
        "fixed_version": patch_info.get("fixed_version"),
        "breaking_changes": patch_info.get("breaking_changes", False)
    })

    # Paso 3: Generar PR de remediación si hay parche
    if patch_info["available"]:
        pr_url = generate_remediation_pr(
            cve_id=cve_id,
            current_version=patch_info["current_version"],
            target_version=patch_info["fixed_version"],
            services=affected_services
        )
        results["steps"].append({
            "step": "remediation_pr",
            "pr_url": pr_url,
            "status": "created"
        })

    # Paso 4: Notificar al equipo
    notify_team(
        channel="#security-incidents",
        summary=f"CVE {cve_id}: {len(affected_services)} servicios afectados. "
                f"Parche {'disponible' if patch_info['available'] else 'NO disponible'}."
    )

    return results
