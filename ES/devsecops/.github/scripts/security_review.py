# Extraído de: LibroDevSecOps/cap-10-code-review-seguridad.md
# .github/scripts/security_review.py
import json
import os
from pathlib import Path

import anthropic
from github import Github

# Configuración desde variables de entorno
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
REPO_NAME = os.environ["REPO_NAME"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)


def get_pr_context() -> dict:
    """Obtiene diff y contenido de ficheros modificados."""
    diff_text = Path("pr_diff.txt").read_text(encoding="utf-8")

    # Recuperar contenido completo de ficheros modificados
    # para que el agente tenga contexto más allá del diff
    modified_files = {}
    for f in pr.get_files():
        if f.status != "removed" and f.filename.endswith(
            (".py", ".ts", ".tsx", ".js", ".jsx", ".yaml", ".yml")
        ):
            try:
                content = repo.get_contents(
                    f.filename, ref=pr.head.sha
                )
                modified_files[f.filename] = content.decoded_content.decode()
            except Exception:
                pass  # Fichero binario o inaccesible

    return {"diff": diff_text, "files": modified_files}
