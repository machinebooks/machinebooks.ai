# Extraído de: LibroDevSecOps/cap-15-seguridad-agentes.md
import os
from pathlib import Path

class ArgumentValidator:
    """Valida argumentos de herramientas contra políticas."""

    def __init__(self, policies: dict[str, dict]):
        self.policies = policies

    def validate(self, tool_name: str, args: dict) -> tuple[bool, str]:
        """Retorna (es_válido, razón_si_inválido)."""
        policy = self.policies.get(tool_name)
        if not policy:
            return True, ""

        for arg_name, constraints in policy.items():
            if arg_name not in args:
                continue

            value = args[arg_name]

            # Validación de ruta: debe estar dentro del directorio permitido
            if "allowed_base_path" in constraints:
                base = Path(constraints["allowed_base_path"]).resolve()
                target = Path(value).resolve()
                if not str(target).startswith(str(base)):
                    return False, (
                        f"Ruta '{value}' fuera del directorio permitido "
                        f"'{base}'"
                    )

            # Validación de patrón: el valor debe coincidir con regex
            if "pattern" in constraints:
                import re
                if not re.match(constraints["pattern"], str(value)):
                    return False, (
                        f"Argumento '{arg_name}' no cumple patrón "
                        f"'{constraints['pattern']}'"
                    )

            # Validación de lista blanca
            if "allowed_values" in constraints:
                if value not in constraints["allowed_values"]:
                    return False, (
                        f"Valor '{value}' no permitido para '{arg_name}'. "
                        f"Valores válidos: {constraints['allowed_values']}"
                    )

        return True, ""

# Ejemplo de políticas para herramientas del pipeline
TOOL_POLICIES = {
    "write_file": {
        "file_path": {
            "allowed_base_path": "/tmp/agent-workspace",
        },
    },
    "execute_scan": {
        "scanner": {
            "allowed_values": ["semgrep", "trivy", "grype", "gitleaks"],
        },
        "target_path": {
            "allowed_base_path": "/workspace/src",
        },
    },
    "create_pull_request": {
        "base_branch": {
            "allowed_values": ["develop", "staging"],
            # No se permite crear PRs directamente contra main
        },
    },
}
