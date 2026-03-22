# Source: The DevSecOps and the Machine -- Chapter 9
# Pattern: Full triage agent with CVE, exposure, and correlation tools

#!/usr/bin/env python3
"""triage_agent.py — Triage agent orchestrator."""
import json
import time
from pathlib import Path

def run_full_triage(findings_dir: str, output_path: str):
    start_time = time.time()

    # 1. Load and normalize findings from all tools
    raw_findings = load_scan_results(Path(findings_dir))
    normalized = [normalize_finding(f) for f in raw_findings]
    print(f"Normalized findings: {len(normalized)}")

    # 2. Apply mandatory OPA policies
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

    print(f"OPA -> immediate action: {len(forced_immediate)}")
    print(f"Sent to agent: {len(agent_queue)}")

    # 3. Group into batches and run agent
    batches = batch_findings(agent_queue)
    agent_results = []
    for i, batch in enumerate(batches):
        print(f"Processing batch {i+1}/{len(batches)} "
              f"({len(batch)} findings)...")
        result = run_triage_agent(batch)
        agent_results.extend(result)

    # 4. Combine OPA + agent results
    all_triaged = forced_immediate + agent_results
    plan = generate_action_plan(all_triaged)

    # 5. Calculate metrics
    elapsed = time.time() - start_time
    plan["triage_duration_seconds"] = round(elapsed, 1)
    plan["triage_timestamp"] = datetime.utcnow().isoformat()

    # 6. Save result
    with open(output_path, "w") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(f"\nTriage completed in {elapsed:.1f}s")
    print(f"Immediate action: {len(plan['immediate_action'])}")
    print(f"Planned action: {len(plan['planned_action'])}")
    print(f"Backlog: {len(plan['backlog'])}")

    return plan