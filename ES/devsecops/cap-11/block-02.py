# Extraído de: LibroDevSecOps/cap-11-remediacion-automatica.md
"""tools_impl.py — Implementación de herramientas con GitHub API."""
from github import Github, GithubException
from functools import lru_cache
import subprocess
import json

# Token con permisos: contents (write), pull_requests (write)
gh = Github("<TU_GITHUB_TOKEN>")
repo = gh.get_repo("<TU_ORG>/<TU_REPO>")

def read_file(file_path: str,
              start_line: int = None,
              end_line: int = None) -> dict:
    """Lee contenido de un fichero del repo."""
    try:
        content = repo.get_contents(file_path, ref="main")
        decoded = content.decoded_content.decode("utf-8")
        lines = decoded.split("\n")

        if start_line and end_line:
            lines = lines[start_line - 1:end_line]

        return {
            "content": "\n".join(lines),
            "total_lines": len(decoded.split("\n")),
            "sha": content.sha
        }
    except GithubException as e:
        return {"error": f"No se pudo leer {file_path}: {e}"}

def create_branch(branch_name: str,
                  base_branch: str = "main") -> dict:
    """Crea rama nueva desde base_branch."""
    try:
        base = repo.get_branch(base_branch)
        ref = repo.create_git_ref(
            f"refs/heads/{branch_name}",
            base.commit.sha
        )
        return {
            "branch": branch_name,
            "sha": ref.object.sha,
            "status": "created"
        }
    except GithubException as e:
        return {"error": f"No se pudo crear rama: {e}"}

def apply_fix(file_path: str,
              new_content: str,
              commit_message: str,
              branch: str) -> dict:
    """Aplica cambio a un fichero en la rama de fix."""
    try:
        # Obtener SHA actual del fichero
        current = repo.get_contents(file_path, ref=branch)
        result = repo.update_file(
            path=file_path,
            message=commit_message,
            content=new_content,
            sha=current.sha,
            branch=branch
        )
        return {
            "commit_sha": result["commit"].sha,
            "status": "applied"
        }
    except GithubException as e:
        return {"error": f"No se pudo aplicar fix: {e}"}

def create_pull_request(title: str,
                        body: str,
                        branch: str,
                        labels: list = None,
                        reviewers: list = None) -> dict:
    """Crea PR con el fix y asigna revisores."""
    try:
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch,
            base="main"
        )
        if labels:
            pr.set_labels(*labels)
        if reviewers:
            pr.create_review_request(reviewers=reviewers)

        return {
            "pr_number": pr.number,
            "pr_url": pr.html_url,
            "status": "created"
        }
    except GithubException as e:
        return {"error": f"No se pudo crear PR: {e}"}
