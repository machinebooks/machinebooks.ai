# Extraído de: LibroConsultor/cap-26-caso-seguridad.md
def generate_executive_report(
    compliance_matrix: list[ControlMapping],
    org_context: dict,
    risk_summary: dict
) -> str:
    """Genera informe ejecutivo desde la matriz de cumplimiento."""

    # Calcular métricas de resumen
    total = len(compliance_matrix)
    compliant = sum(1 for c in compliance_matrix if c.status == "compliant")
    partial = sum(1 for c in compliance_matrix if c.status == "partial")
    non_compliant = sum(1 for c in compliance_matrix if c.status == "non_compliant")

    compliance_rate = (compliant / total) * 100

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system="""Genera un informe ejecutivo de auditoría ISO 27001
        para un Comité de Dirección. Máximo 12 páginas.
        Incluir: resumen ejecutivo, nivel de cumplimiento global,
        hallazgos críticos (máx 5), mapa de riesgos, plan de acción
        con prioridades y plazos.
        Tono: profesional, directo, orientado a decisiones.
        NO incluir detalles técnicos — eso va en el informe técnico.
        Idioma: español.""",
        messages=[{"role": "user", "content": f"""
        Contexto de la organización:
        {json.dumps(org_context, ensure_ascii=False)}

        Cumplimiento global: {compliance_rate:.1f}%
        Conformes: {compliant}, Parciales: {partial}, No conformes: {non_compliant}

        Resumen de riesgos:
        {json.dumps(risk_summary, ensure_ascii=False)}

        Hallazgos no conformes (detalle):
        {json.dumps([c.__dict__ for c in compliance_matrix
                     if c.status != "compliant"],
                    ensure_ascii=False, indent=2)}"""}]
    )
    return response.content[0].text
