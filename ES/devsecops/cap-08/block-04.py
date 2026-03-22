# Extraído de: LibroDevSecOps/cap-08-orquestacion-pipeline.md
def main():
    parser = argparse.ArgumentParser(description="Security aggregator")
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    all_findings: list[Finding] = []

    # Parsers mapeados a las rutas de artefactos
    parsers = {
        "sast-results/sast-results.json": parse_semgrep,
        "sca-results/sca-results.json": parse_grype,
        "secrets-results/secrets-results.json": parse_gitleaks,
        "container-results/container-results.json": parse_trivy,
    }

    for rel_path, parse_fn in parsers.items():
        full_path = results_dir / rel_path
        if full_path.exists():
            try:
                all_findings.extend(parse_fn(full_path))
                print(f"[OK] Parsed {rel_path}: "
                      f"{len(parse_fn(full_path))} findings")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[ERROR] Failed to parse {rel_path}: {e}")
        else:
            print(f"[WARN] Missing results: {rel_path}")

    # Aplica el gate
    report = apply_gate(all_findings)
    report.pr_comment = generate_pr_comment(report)

    # Serializa el informe
    output_data = {
        "gate_decision": report.gate_decision,
        "block_reason": report.block_reason,
        "summary": report.summary,
        "pr_comment": report.pr_comment,
        "findings": [
            {
                "source": f.source,
                "severity": f.severity,
                "title": f.title,
                "location": f.location,
                "cve_id": f.cve_id,
                "fixable": f.fixable,
            }
            for f in report.findings
        ],
    }

    Path(args.output).write_text(json.dumps(output_data, indent=2))
    print(f"\nGate decision: {report.gate_decision.upper()}")
    print(f"Total findings: {report.summary['total']}")


if __name__ == "__main__":
    main()
