# Source: The DevSecOps and the Machine -- Chapter 3
# Pattern: Continuous attack surface discovery with Claude Agent SDK

"""
surface_discovery_agent.py — Claude agent that discovers changes
in the attack surface between executions, classifies new
assets with STRIDE, and generates change alerts.
"""
from claude_agent_sdk import Agent, tool
import json
from pathlib import Path
from datetime import datetime

@tool
def scan_pipeline_assets(project_root: str) -> dict:
    """Run the pipeline asset inventory.
    Returns the list of discovered assets with metadata."""
    from pipeline_inventory import run_inventory
    assets = run_inventory(Path(project_root))
    return {"assets": [_asset_to_dict(a) for a in assets],
            "timestamp": datetime.utcnow().isoformat()}

@tool
def load_previous_inventory(inventory_path: str) -> dict:
    """Load the inventory from the previous execution for comparison."""
    path = Path(inventory_path)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"assets": [], "timestamp": None}

@tool
def diff_inventories(current: list[dict], previous: list[dict]) -> dict:
    """Compare two inventories and detect new, removed,
    and modified assets."""
    current_names = {a["name"] for a in current}
    previous_names = {a["name"] for a in previous}
    added = [a for a in current if a["name"] in current_names - previous_names]
    removed = [a for a in previous if a["name"] in previous_names - current_names]
    # Detect changes in existing assets
    prev_map = {a["name"]: a for a in previous}
    modified = []
    for asset in current:
        if asset["name"] in prev_map:
            prev = prev_map[asset["name"]]
            if asset.get("exposed") != prev.get("exposed"):
                modified.append({
                    "asset": asset["name"],
                    "change": "exposure_changed",
                    "from": prev.get("exposed"),
                    "to": asset.get("exposed")
                })
            if asset.get("metadata") != prev.get("metadata"):
                modified.append({
                    "asset": asset["name"],
                    "change": "metadata_changed",
                    "details": "Configuration modified"
                })
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "summary": (
            f"{len(added)} new, {len(removed)} removed, "
            f"{len(modified)} modified"
        )
    }

@tool
def classify_new_assets_stride(assets: list[dict]) -> list[dict]:
    """Apply STRIDE classification to newly discovered assets."""
    from stride_classifier import run_stride_analysis
    return run_stride_analysis(assets)

@tool
def save_inventory(inventory: dict, output_path: str) -> str:
    """Persist the current inventory for the next comparison."""
    with open(output_path, "w") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    return f"Inventory saved to {output_path}"

# Agent configuration
agent = Agent(
    model="claude-sonnet-4-6",
    tools=[
        scan_pipeline_assets,
        load_previous_inventory,
        diff_inventories,
        classify_new_assets_stride,
        save_inventory,
    ],
    system_prompt="""You are an attack surface discovery agent.
Your job is:
1. Run the pipeline asset inventory.
2. Compare with the previous inventory.
3. For NEW assets, run STRIDE classification.
4. Generate a report with detected changes and new asset threats.
5. Save the updated inventory.

Prioritize exposed assets (exposed=true) and AI assets
(llm_endpoint, rag_corpus, agent_tool).
If an asset changes from unexposed to exposed, mark it as a critical change."""
)

def _asset_to_dict(asset) -> dict:
    """Convert an Asset dataclass to dictionary."""
    from dataclasses import asdict
    return asdict(asset)