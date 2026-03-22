# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
import json
import yaml
import os
from pathlib import Path

# Directorio base para especificaciones OpenAPI
SPECS_BASE_DIR = Path(os.environ.get("SPECS_BASE_DIR", "specs")).resolve()
ALLOWED_SPEC_EXTENSIONS = {".yaml", ".yml", ".json"}

def parse_openapi_spec(spec_path: str) -> dict:
    """Analiza una especificación OpenAPI y extrae la superficie de ataque.

    Valida la ruta contra SPECS_BASE_DIR para prevenir
    ataques de path traversal.
    """
    resolved = Path(spec_path).resolve()
    if not resolved.is_relative_to(SPECS_BASE_DIR):
        raise ValueError(
            f"Acceso denegado: '{spec_path}' está fuera del directorio permitido."
        )
    if resolved.suffix.lower() not in ALLOWED_SPEC_EXTENSIONS:
        raise ValueError(
            f"Tipo de fichero no soportado: '{resolved.suffix}'. "
            f"Permitidos: {', '.join(ALLOWED_SPEC_EXTENSIONS)}"
        )

    with open(str(resolved)) as f:
        if resolved.suffix.lower() in (".yaml", ".yml"):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)

    endpoints = []
    security_schemes = spec.get("components", {}).get("securitySchemes", {})

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                params = []
                # Parámetros de ruta y query
                for p in details.get("parameters", []):
                    params.append({
                        "name": p["name"],
                        "in": p["in"],
                        "type": p.get("schema", {}).get("type", "string"),
                        "required": p.get("required", False),
                    })
                # Cuerpo de la petición
                request_body = details.get("requestBody", {})
                body_schema = {}
                if request_body:
                    content = request_body.get("content", {})
                    json_content = content.get("application/json", {})
                    body_schema = json_content.get("schema", {})

                # Seguridad del endpoint
                endpoint_security = details.get("security", spec.get("security", []))

                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "parameters": params,
                    "body_schema": body_schema,
                    "security": endpoint_security,
                    "tags": details.get("tags", []),
                    "summary": details.get("summary", ""),
                })

    return {
        "base_url": spec.get("servers", [{}])[0].get("url", ""),
        "endpoints": endpoints,
        "security_schemes": security_schemes,
        "total_endpoints": len(endpoints),
    }
