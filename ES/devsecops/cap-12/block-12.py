# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
def run_nuclei_checks(
    target_url: str,
    tech_stack: list[str],
) -> dict:
    """Ejecuta templates de Nuclei relevantes para el stack tecnológico."""
    # Mapear stack a templates de Nuclei
    template_map = {
        "fastapi": ["http/technologies/fastapi-detect.yaml"],
        "nginx": [
            "http/misconfiguration/nginx/",
            "http/cves/nginx/",
        ],
        "postgresql": ["network/cves/postgresql/"],
        "redis": [
            "network/exposed-redis.yaml",
            "network/cves/redis/",
        ],
        "docker": ["http/exposures/configs/docker-compose-exposure.yaml"],
    }

    templates = []
    for tech in tech_stack:
        templates.extend(template_map.get(tech.lower(), []))

    if not templates:
        return {"skipped": True, "reason": "No hay templates para el stack"}

    template_args = []
    for t in templates:
        template_args.extend(["-t", t])

    cmd = [
        "docker", "run", "--rm",
        "--network", "host",
        "projectdiscovery/nuclei:latest",
        "-u", target_url,
        "-json",
        "-severity", "medium,high,critical",
    ] + template_args

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    findings = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                findings.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return {"findings": findings, "total": len(findings)}
