# Extraído de: LibroConsultor/cap-06-generacion-entregables.md
class ComplianceMatrixGenerator:
    """Genera matrices de cumplimiento control por control."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-6"

    def generate_control_assessment(
        self, control: dict, evidence: dict, context: str
    ) -> dict:
        """Evalúa un control individual contra las evidencias."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="""Eres un auditor evaluando un control de
seguridad. Responde SOLO en JSON con esta estructura:
{
  "control_id": "...",
  "status": "cumple|cumple_parcial|no_cumple",
  "evidence_summary": "...",
  "gap_description": "..." o null,
  "risk_level": "alto|medio|bajo",
  "remediation": "...",
  "effort_hours": N,
  "priority": "quick_win|medio_plazo|largo_plazo"
}
Sé directo. No uses hedging. Si no cumple, di que no cumple.""",
            messages=[{
                "role": "user",
                "content": f"""CONTROL:
ID: {control['id']}
Título: {control['title']}
Descripción: {control['description']}
Criterio de cumplimiento: {control['criteria']}

EVIDENCIAS DEL CLIENTE:
{evidence.get('description', 'No se proporcionó evidencia')}

CONTEXTO DEL ASSESSMENT:
{context}

Evalúa este control."""
            }]
        )
        # Parsear respuesta JSON
        import json
        return json.loads(response.content[0].text)

    def generate_matrix(
        self, controls: list[dict], evidences: dict, context: str
    ) -> list[dict]:
        """Genera la matriz completa, control por control."""
        results = []
        for control in controls:
            evidence = evidences.get(control["id"], {})
            assessment = self.generate_control_assessment(
                control, evidence, context
            )
            results.append(assessment)
        return results
