# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
    def evaluate_control(self, control: AuditControl) -> AuditControl:
        """Evalúa un control contra las evidencias disponibles."""
        # Buscar documentos relacionados con este control
        relevant_docs = self._find_relevant_docs(control)

        if not relevant_docs:
            control.status = "no_cumple"
            control.justification = (
                "No se encontró documentación que evidencie "
                f"la implementación de {control.title}."
            )
            return control

        # Construir contexto con evidencias relevantes
        evidence_context = "\n\n---\n\n".join([
            f"**Documento: {name}**\n{content[:4000]}"
            for name, content in relevant_docs.items()
        ])

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=f"""Eres un auditor experto en {self.framework}.
Evalúa si las evidencias presentadas demuestran cumplimiento
del control indicado.

Reglas:
- Si la evidencia demuestra cumplimiento completo: "cumple"
- Si la evidencia es parcial o desactualizada: "parcial"
- Si no hay evidencia suficiente: "no_cumple"
- Si el control no aplica al contexto: "no_aplica"
- SIEMPRE incluye cita textual de la evidencia relevante
- SIEMPRE justifica tu evaluación con hechos del documento
- NUNCA inventes evidencia que no esté en los documentos""",
            messages=[{
                "role": "user",
                "content": f"""Control: {control.control_id} — {control.title}
Descripción: {control.description}

Evidencias disponibles:
{evidence_context}

Responde en JSON:
{{
  "status": "cumple|parcial|no_cumple|no_aplica",
  "justification": "explicación detallada",
  "evidence_quotes": ["citas textuales del documento"],
  "gaps_identified": ["lagunas detectadas"],
  "risk_if_not_addressed": "riesgo si no se remedia"
}}"""
            }]
        )

        result = json.loads(response.content[0].text)
        control.status = result["status"]
        control.justification = result["justification"]
        control.evidence_refs = [
            name for name in relevant_docs.keys()
        ]
        return control
