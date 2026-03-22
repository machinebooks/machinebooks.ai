# Source: The DevSecOps and the Machine -- Chapter 3
# Pattern: Automated asset discovery (Docker, GitHub Actions, LLM, RAG)

"""
pipeline_inventory.py — Automated pipeline asset inventory.
Traverses configuration sources and generates a structured JSON
with each asset, its category, and exposure metadata.
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
    source_file: str       # File where the asset was discovered
    exposed: bool = False  # Accessible from outside the perimeter?
    metadata: dict = field(default_factory=dict)

def discover_docker_services(compose_path: Path) -> list[Asset]:
    """Extract services, images, and ports from docker-compose.yml."""
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
    """Extract steps, third-party actions, and secrets from workflows."""
    assets = []
    for wf_file in workflows_dir.glob("*.yml"):
        with open(wf_file) as f:
            wf = yaml.safe_load(f)
        for job_name, job in wf.get("jobs", {}).items():
            for step in job.get("steps", []):
                if "uses" in step:
                    # Third-party action: supply chain surface
                    action = step["uses"]
                    assets.append(Asset(
                        name=f"action:{action}",
                        category="build_system",
                        source_file=str(wf_file),
                        metadata={"job": job_name, "action": action}
                    ))
        # Detect secrets referenced in the workflow
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
    """Search for LLM API calls in source code."""
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
                    exposed=True,  # Assume exposed until confirmed
                    metadata={"api_type": api_type, "occurrences": len(matches)}
                ))
    return assets

def discover_rag_config(source_dir: Path) -> list[Asset]:
    """Search for RAG configurations: vector database connections."""
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
    """Run all discoverers and consolidate the inventory."""
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
    print(f"\n--- {len(inventory)} assets discovered ---")