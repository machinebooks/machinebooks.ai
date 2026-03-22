# Extraído de: LibroDevSecOps/cap-26-caso-pipeline.md
def generate_remediation_pr(finding: dict, repo: str) -> str:
    """Genera una PR de remediación para un hallazgo de seguridad."""
    # Obtener el código afectado
    source_code = get_file_content(repo, finding["file"], finding["line_range"])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=(
            "Eres un agente de remediación de seguridad. Genera un fix "
            "mínimo y seguro para la vulnerabilidad descrita. El fix debe: "
            "1) resolver la vulnerabilidad, 2) no romper funcionalidad "
            "existente, 3) incluir un comentario explicativo, 4) seguir "
            "las convenciones del código existente."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Vulnerabilidad: {finding['rule_id']}\n"
                f"Severidad: {finding['severity']}\n"
                f"Descripción: {finding['message']}\n"
                f"Archivo: {finding['file']}\n"
                f"Código afectado:\n