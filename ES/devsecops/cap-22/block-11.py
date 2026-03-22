# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
class AuditPreparationAgent:
    """Agente que prepara el paquete de evidencias para auditoría."""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def prepare_audit_package(
        self,
        framework: str,
        assessments: list[ControlAssessment],
        audit_scope: str,
    ) -> dict:
        """Genera el paquete completo para el auditor."""

        controls_summary = []
        for a in assessments:
            controls_summary.append({
                "control_id": a.control.control_id,
                "title": a.control.title,
                "status": a.status.value,
                "evidence_count": len(a.evidences),
                "latest_evidence_date": max(
                    (e.timestamp for e in a.evidences), default=None
                ),
                "justification": a.justification,
            })

        prompt = f"""Eres un consultor de compliance preparando una \
auditoría de {framework}.

## Alcance de la auditoría
{audit_scope}

## Estado actual de los controles
{json.dumps(controls_summary, indent=2, ensure_ascii=False, default=str)}

Genera:
1. Un resumen ejecutivo de 200 palabras para el auditor.
2. Para cada control NO cumplido: plan de remediación con plazo.
3. Para cada control PARCIAL: qué evidencia adicional se necesita.
4. Las 5 preguntas más probables del auditor y respuestas sugeridas.
5. Riesgos del proceso de auditoría: qué puede salir mal.

Responde en JSON con las claves: executive_summary,
remediation_plans, partial_actions, expected_questions,
audit_risks."""

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        result = json.loads(response.content[0].text)

        # Registrar decisión del agente
        self._log_agent_decision(
            action="audit_preparation",
            framework=framework,
            controls_evaluated=len(assessments),
            model="claude-sonnet-4-6",
        )

        return result

    def _log_agent_decision(self, **kwargs) -> None:
        """Registra decisión para trazabilidad de auditoría."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "audit-preparation",
            **kwargs,
        }
        log_path = Path("logs/agent-decisions.jsonl")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
