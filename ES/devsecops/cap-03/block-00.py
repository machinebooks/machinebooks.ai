# Extraído de: LibroDevSecOps/cap-03-mapa-superficie-ataque.md
"""
pipeline_inventory.py — Inventario automatizado de activos del pipeline.
Recorre fuentes de configuración y genera un JSON estructurado
con cada activo, su categoría y metadatos de exposición.
"""
import yaml
import json
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class Asset:
    name: str
    category: str          # code_repo, build_system, container, secret,
                           # api_endpoint, llm_endpoint, rag_corpus, agent_tool
    source_file: str       # Fichero donde se descubrió el activo
    exposed: bool = False  # ¿Accesible desde fuera del perímetro?
    metadata: dict = field(default_factory=dict)

def discover_docker_services(compose_path: Path) -> list[Asset]:
    """Extrae servicios, imágenes y puertos de docker-compose.yml."""
    assets = []
    with open(compose_path) as f:
        compose = yaml.safe_load(f)
    for name, svc in compose.get("services", {}).items():
        ports = svc.get("ports", [])
        exposed = any(":" in str(p) for p in ports)
        assets.append(Asset(
            name=f"container:{name}",
            category="container",
            source_file=str(compose_path),
            exposed=exposed,
            metadata={
                "image": svc.get("image", "build-local"),
                "ports": ports,
                "volumes": svc.get("volumes", []),
                "privileged": svc.get("privileged", False),
            }
        ))
    return assets

def discover_github_actions(workflows_dir: Path) -> list[Asset]:
    """Extrae steps, acciones de terceros y secrets de los workflows."""
    assets = []
    for wf_file in workflows_dir.glob("*.yml"):
        with open(wf_file) as f:
            wf = yaml.safe_load(f)
        for job_name, job in wf.get("jobs", {}).items():
            for step in job.get("steps", []):
                if "uses" in step:
                    # Acción de terceros: superficie de supply chain
                    action = step["uses"]
                    assets.append(Asset(
                        name=f"action:{action}",
                        category="build_system",
                        source_file=str(wf_file),
                        metadata={"job": job_name, "action": action}
                    ))
        # Detectar secrets referenciados en el workflow
        wf_text = wf_file.read_text()
        secrets = set(re.findall(r"\$\{\{\s*secrets\.(\w+)\s*\}\}", wf_text))
        for secret in secrets:
            assets.append(Asset(
                name=f"secret:{secret}",
                category="secret",
                source_file=str(wf_file),
                metadata={"referenced_in": str(wf_file)}
            ))
    return assets

def discover_llm_endpoints(source_dir: Path) -> list[Asset]:
    """Busca llamadas a APIs de LLM en el código fuente."""
    assets = []
    patterns = [
        (r"client\.messages\.create\(", "anthropic_api"),
        (r"openai\.ChatCompletion\.create\(", "openai_api"),
        (r"anthropic\.Anthropic\(", "anthropic_client"),
        (r"model\s*=\s*[\"']claude-", "claude_model"),
    ]
    for py_file in source_dir.rglob("*.py"):
        content = py_file.read_text(errors="ignore")
        for pattern, api_type in patterns:
            matches = re.findall(pattern, content)
            if matches:
                assets.append(Asset(
                    name=f"llm_endpoint:{py_file.stem}:{api_type}",
                    category="llm_endpoint",
                    source_file=str(py_file),
                    exposed=True,  # Asumir expuesto hasta confirmar
                    metadata={"api_type": api_type, "occurrences": len(matches)}
                ))
    return assets

def discover_rag_config(source_dir: Path) -> list[Asset]:
    """Busca configuraciones de RAG: conexiones a bases vectoriales."""
    assets = []
    rag_patterns = [
        (r"QdrantClient\(", "qdrant"),
        (r"chromadb\.Client\(", "chroma"),
        (r"pinecone\.init\(", "pinecone"),
        (r"collection\.add\(", "vector_store"),
    ]
    for py_file in source_dir.rglob("*.py"):
        content = py_file.read_text(errors="ignore")
        for pattern, store_type in rag_patterns:
            if re.search(pattern, content):
                assets.append(Asset(
                    name=f"rag_corpus:{py_file.stem}:{store_type}",
                    category="rag_corpus",
                    source_file=str(py_file),
                    metadata={"vector_store": store_type}
                ))
    return assets

def run_inventory(project_root: Path) -> list[Asset]:
    """Ejecuta todos los descubridores y consolida el inventario."""
    assets = []
    compose = project_root / "docker-compose.yml"
    if compose.exists():
        assets.extend(discover_docker_services(compose))
    wf_dir = project_root / ".github" / "workflows"
    if wf_dir.exists():
        assets.extend(discover_github_actions(wf_dir))
    src_dir = project_root / "src"
    if src_dir.exists():
        assets.extend(discover_llm_endpoints(src_dir))
        assets.extend(discover_rag_config(src_dir))
    return assets

if __name__ == "__main__":
    root = Path(".")
    inventory = run_inventory(root)
    output = [asdict(a) for a in inventory]
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n--- {len(inventory)} activos descubiertos ---")
