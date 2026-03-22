# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
import json
from pathlib import Path
from claude_agent_sdk import Agent, tool
from dataclasses import dataclass, asdict

@dataclass
class Finding:
    """Hallazgo estructurado de análisis."""
    framework_ref: str      # Ej: "ISO 27001 A.8.2"
    status: str             # conforme | parcial | no_conforme | no_aplica
    evidencia: str          # Resumen de evidencia analizada
    gap: str                # Discrepancia detectada
    riesgo: str             # crítico | alto | medio | bajo
    recomendacion: str      # Acción para cerrar el gap
    confianza: float        # 0.0 a 1.0

@tool
def query_framework(
    framework: str,
    section: str
) -> dict:
    """Consulta un framework de referencia y devuelve los requisitos
    de una sección o control específico.

    Args:
        framework: Nombre del framework (iso27001, ens, dora)
        section: Sección o control a consultar (ej: 'A.8.2', '8.1')
    """
    # Carga el framework desde ficheros JSON estructurados
    framework_path = Path(f"frameworks/{framework}/{section}.json")
    if not framework_path.exists():
        return {"error": f"Sección {section} no encontrada en {framework}"}

    with open(framework_path) as f:
        control = json.load(f)

    return {
        "framework": framework,
        "section": section,
        "title": control["title"],
        "requirements": control["requirements"],
        "guidance": control.get("guidance", ""),
        "related_controls": control.get("related", [])
    }
