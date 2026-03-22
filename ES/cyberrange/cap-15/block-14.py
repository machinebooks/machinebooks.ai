# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
# Ejemplo didáctico: generación de informe MITRE post-ejercicio
async def generate_mitre_report(db: Session, scenario_id: int):
    """Genera un mapa de cobertura MITRE ATT&CK del ejercicio."""
    executions = db.query(AttackExecution).filter(
        AttackExecution.scenario_id == scenario_id,
        AttackExecution.state.in_(["success", "failed"])
    ).all()

    coverage = {}
    for exec in executions:
        tpl = db.query(ActionTemplate).get(exec.action_template_id)
        if tpl and tpl.mitre_technique_id:
            technique = tpl.mitre_technique_id
            if technique not in coverage:
                coverage[technique] = {
                    "technique": technique,
                    "tactic": tpl.mitre_tactic,
                    "name": tpl.name,
                    "attempts": 0,
                    "successes": 0,
                    "kill_chain_phase": tpl.kill_chain_phase,
                }
            coverage[technique]["attempts"] += 1
            if exec.state == "success":
                coverage[technique]["successes"] += 1

    return {
        "scenario_id": scenario_id,
        "total_techniques": len(coverage),
        "coverage": sorted(
            coverage.values(),
            key=lambda x: x["tactic"]
        ),
        "tactics_covered": list(set(
            t["tactic"] for t in coverage.values()
        ))
    }
