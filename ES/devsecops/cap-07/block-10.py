# Extraído de: LibroDevSecOps/cap-07-contenedores.md
from claude_agent_sdk import Agent, tool
import subprocess
import json

@tool
def get_current_dockerfile(path: str = "Dockerfile") -> str:
    """Lee el Dockerfile actual del repositorio."""
    with open(path) as f:
        return f.read()

@tool
def check_base_image_tags(image: str) -> list:
    """Consulta los tags disponibles para una imagen base."""
    # Simula consulta al registro (en producción: API de Docker Hub)
    result = subprocess.run(
        ["trivy", "image", "--list-all-pkgs", "--format", "json",
         f"{image}"],
        capture_output=True, text=True, timeout=60
    )
    return json.loads(result.stdout) if result.returncode == 0 else {}

@tool
def scan_dockerfile(content: str) -> dict:
    """Escanea un Dockerfile con Trivy config mode."""
    tmp_path = "/tmp/Dockerfile.candidate"
    with open(tmp_path, "w") as f:
        f.write(content)
    result = subprocess.run(
        ["trivy", "config", "--format", "json", tmp_path],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout) if result.returncode == 0 else {}

# Configuración del agente de remediación
remediation_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[get_current_dockerfile, check_base_image_tags,
           scan_dockerfile],
    system="""Eres un agente de remediación de seguridad de
contenedores. Tu objetivo: dado un informe de Trivy, generar
un Dockerfile corregido que elimine o mitigue los hallazgos.
Prioridades: 1) cambiar imagen base si reduce >50% de CVEs,
2) eliminar paquetes innecesarios, 3) aplicar multi-stage build
si no existe, 4) configurar usuario non-root. Siempre valida
el Dockerfile generado con scan_dockerfile antes de proponerlo.""",
)
