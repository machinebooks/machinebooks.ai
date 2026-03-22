# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
def detect_access_control_issues(
    results_admin: dict,
    results_standard: dict,
) -> list[dict]:
    """Compara resultados de dos perfiles para detectar control de acceso roto."""
    admin_endpoints = {
        (a["url"], a["method"])
        for a in results_admin.get("accessible_endpoints", [])
    }
    standard_endpoints = {
        (a["url"], a["method"])
        for a in results_standard.get("accessible_endpoints", [])
    }

    # Endpoints que el usuario estándar NO debería alcanzar
    admin_only = admin_endpoints - standard_endpoints
    issues = []

    for url, method in standard_endpoints:
        if (url, method) in admin_only:
            continue
        # Verificar si el usuario estándar accede a datos de otros usuarios
        if "/admin" in url or "/management" in url:
            issues.append({
                "type": "broken_access_control",
                "endpoint": f"{method} {url}",
                "severity": "HIGH",
                "description": "Endpoint administrativo accesible con perfil estándar",
                "cwe": "CWE-284",
            })

    return issues
