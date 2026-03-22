# Extraído de: LibroBugBounty/cap-12-prompt-injection-rce.md
import os
from pathlib import Path

def scan_accessible_secrets():
    """Enumera secretos accesibles desde el contexto del developer."""
    home = Path.home()
    findings = []

    # SSH keys
    ssh_dir = home / ".ssh"
    if ssh_dir.exists():
        for key_file in ssh_dir.glob("id_*"):
            if not key_file.name.endswith(".pub"):
                findings.append(("SSH_KEY", str(key_file)))

    # AWS credentials
    aws_creds = home / ".aws" / "credentials"
    if aws_creds.exists():
        findings.append(("AWS_CREDENTIALS", str(aws_creds)))

    # Azure CLI tokens
    azure_dir = home / ".azure"
    if azure_dir.exists():
        for token_file in azure_dir.glob("*token*"):
            findings.append(("AZURE_TOKEN", str(token_file)))

    # .env files en proyectos comunes
    for dev_dir in [home / "Projects", home / "repos",
                    home / "src", home / "code"]:
        if dev_dir.exists():
            for env_file in dev_dir.rglob(".env"):
                findings.append(("ENV_FILE", str(env_file)))

    # Git credentials
    git_creds = home / ".git-credentials"
    if git_creds.exists():
        findings.append(("GIT_CREDENTIALS", str(git_creds)))

    # NPM tokens
    npmrc = home / ".npmrc"
    if npmrc.exists():
        content = npmrc.read_text()
        if "authToken" in content or "_auth" in content:
            findings.append(("NPM_TOKEN", str(npmrc)))

    return findings
