# Source: The DevSecOps and the Machine -- Chapter 7
# Pattern: Dockerfile remediation agent with Claude Agent SDK

from claude_agent_sdk import Agent, tool
import subprocess
import json

@tool
def get_current_dockerfile(path: str = "Dockerfile") -> str:
    """Read the current Dockerfile from the repository."""
    with open(path) as f:
        return f.read()

@tool
def check_base_image_tags(image: str) -> list:
    """Query available tags for a base image."""
    # Simulates registry query (in production: Docker Hub API)
    result = subprocess.run(
        ["trivy", "image", "--list-all-pkgs", "--format", "json",
         f"{image}"],
        capture_output=True, text=True, timeout=60
    )
    return json.loads(result.stdout) if result.returncode == 0 else {}

@tool
def scan_dockerfile(content: str) -> dict:
    """Scan a Dockerfile with Trivy config mode."""
    tmp_path = "/tmp/Dockerfile.candidate"
    with open(tmp_path, "w") as f:
        f.write(content)
    result = subprocess.run(
        ["trivy", "config", "--format", "json", tmp_path],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout) if result.returncode == 0 else {}

# Remediation agent configuration
remediation_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[get_current_dockerfile, check_base_image_tags,
           scan_dockerfile],
    system="""You are a container security remediation agent.
Your goal: given a Trivy report, generate a corrected
Dockerfile that eliminates or mitigates the findings.
Priorities: 1) change base image if it reduces >50% of CVEs,
2) remove unnecessary packages, 3) apply multi-stage build
if none exists, 4) configure non-root user. Always validate
the generated Dockerfile with scan_dockerfile before proposing it.""",
)
