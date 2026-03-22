# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
def findings_to_report_section(findings: list[AuditFinding]) -> str:
    """Convierte hallazgos del agente en sección de informe."""
    client = anthropic.Anthropic()

    findings_json = json.dumps(
        [vars(f) for f in findings], indent=2, ensure_ascii=False
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system="""Eres un redactor de informes de auditoría profesional.
Transforma los hallazgos estructurados en prosa formal de informe,
manteniendo la precisión técnica y la trazabilidad a evidencias.
Idioma: español técnico. Tono: objetivo, sin juicios de valor innecesarios.
Cada hallazgo debe incluir: descripción, evidencia, riesgo y recomendación.""",
        messages=[{
            "role": "user",
            "content": f"Hallazgos a redactar:\n{findings_json}"
        }]
    )

    return response.content[0].text
