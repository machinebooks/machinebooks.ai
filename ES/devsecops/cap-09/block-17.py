# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
#!/usr/bin/env python3
"""triage_agent.py — Orquestador del agente de triaje."""
import json
import time
from pathlib import Path

def run_full_triage(findings_dir: str, output_path: str):
    start_time = time.time()

    # 1. Cargar y normalizar hallazgos de todas las herramientas
    raw_findings = load_scan_results(Path(findings_dir))
    normalized = [normalize_finding(f) for f in raw_findings]
    print(f"Hallazgos normalizados: {len(normalized)}")

    # 2. Aplicar políticas OPA obligatorias
    forced_immediate = []
    agent_queue = []
    for finding in normalized:
        opa_result = evaluate_opa_policies(finding)
        if opa_result.get("force_immediate"):
            finding["priority_score"] = 95
            finding["reasoning"] = opa_result["message"]
            forced_immediate.append(finding)
        else:
            finding["opa_constraints"] = opa_result
            agent_queue.append(finding)

    print(f"OPA -> acción inmediata: {len(forced_immediate)}")
    print(f"Enviados al agente: {len(agent_queue)}")

    # 3. Agrupar en lotes y ejecutar agente
    batches = batch_findings(agent_queue)
    agent_results = []
    for i, batch in enumerate(batches):
        print(f"Procesando lote {i+1}/{len(batches)} "
              f"({len(batch)} hallazgos)...")
        result = run_triage_agent(batch)
        agent_results.extend(result)

    # 4. Combinar resultados de OPA + agente
    all_triaged = forced_immediate + agent_results
    plan = generate_action_plan(all_triaged)

    # 5. Calcular métricas
    elapsed = time.time() - start_time
    plan["triage_duration_seconds"] = round(elapsed, 1)
    plan["triage_timestamp"] = datetime.utcnow().isoformat()

    # 6. Guardar resultado
    with open(output_path, "w") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(f"\nTriaje completado en {elapsed:.1f}s")
    print(f"Acción inmediata: {len(plan['immediate_action'])}")
    print(f"Acción planificada: {len(plan['planned_action'])}")
    print(f"Backlog: {len(plan['backlog'])}")

    return plan
