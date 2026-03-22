# Extraído de: LibroDevSecOps/cap-10-code-review-seguridad.md
def publish_findings(findings: list[dict]) -> None:
    """Publica hallazgos como review comments en la PR."""
    if not findings:
        # Sin hallazgos: dejar un comentario general positivo
        pr.create_issue_comment(
            "🔒 **Security Review (AI)**: No se detectaron "
            "patrones inseguros en esta PR.\n\n"
            "_Revisión automática con Claude claude-sonnet-4-6. "
            "No sustituye la revisión humana de seguridad._"
        )
        return

    # Obtener el último commit de la PR para posicionar comments
    commit = repo.get_commit(pr.head.sha)

    comments_body = []
    for finding in findings:
        severity_icon = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
        }.get(finding["severity"], "⚪")

        body = (
            f"{severity_icon} **[{finding['category']}]** "
            f"Severidad: {finding['severity']} | "
            f"Confianza: {finding['confidence']}\n\n"
            f"{finding['explanation']}\n\n"
        )

        if finding.get("suggested_fix"):
            body += (
                f"**Fix sugerido:**\n"
                f"