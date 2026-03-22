# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
import anthropic
import json


class ComplianceGapAnalyzer:
    """Agente que analiza diferencias entre versiones de un framework."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-6"

    def analyze_framework_update(
        self,
        framework_name: str,
        old_controls: list[dict],
        new_controls: list[dict],
        current_mappings: list[dict],
    ) -> dict:
        """Analiza el impacto de una actualización de framework."""

        prompt = f"""Eres un consultor de compliance con experiencia en \
{framework_name}.

Analiza la actualización entre dos versiones del framework.

## Controles de la versión anterior
{json.dumps(old_controls, indent=2, ensure_ascii=False)}

## Controles de la nueva versión
{json.dumps(new_controls, indent=2, ensure_ascii=False)}

## Mapeos actuales de evidencia automatizada
{json.dumps(current_mappings, indent=2, ensure_ascii=False)}

Genera un análisis de gaps con esta estructura JSON:
{{
  "new_controls": [
    {{
      "control_id": "id del nuevo control",
      "title": "título",
      "impact": "descripción del impacto en el pipeline",
      "suggested_evidence_sources": ["fuentes sugeridas"],
      "automation_feasible": true/false,
      "effort_estimate": "low/medium/high"
    }}
  ],
  "modified_controls": [
    {{
      "old_id": "id anterior",
      "new_id": "id nuevo",
      "change_description": "qué cambió",
      "mapping_impact": "cómo afecta al mapeo existente",
      "action_required": "qué hay que hacer"
    }}
  ],
  "removed_controls": [
    {{
      "control_id": "id eliminado",
      "replacement": "control que lo sustituye o null"
    }}
  ],
  "summary": {{
    "total_new": 0,
    "total_modified": 0,
    "total_removed": 0,
    "estimated_effort_days": 0,
    "risk_assessment": "texto libre"
  }}
}}

Responde SOLO con el JSON, sin texto adicional."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        result = json.loads(response.content[0].text)

        # Registrar la decisión del agente para auditoría
        self._log_agent_decision(
            framework=framework_name,
            input_controls_old=len(old_controls),
            input_controls_new=len(new_controls),
            result_summary=result.get("summary", {}),
            model=self.model,
            tokens_used=(
                response.usage.input_tokens + response.usage.output_tokens
            ),
        )

        return result

    def suggest_control_mapping(
        self,
        control: dict,
        available_evidence_sources: list[str],
    ) -> dict:
        """Sugiere mapeo de evidencia para un control nuevo."""

        prompt = f"""Dado este control normativo:
{json.dumps(control, indent=2, ensure_ascii=False)}

Y estas fuentes de evidencia disponibles en el pipeline DevSecOps:
{json.dumps(available_evidence_sources, indent=2)}

Sugiere qué fuentes de evidencia demuestran el cumplimiento
de este control. Para cada fuente, explica qué criterio de
aceptación debería aplicarse.

Responde en JSON:
{{
  "control_id": "...",
  "suggested_mappings": [
    {{
      "evidence_source": "...",
      "pass_criteria": "...",
      "confidence": "high/medium/low",
      "reasoning": "..."
    }}
  ],
  "manual_evidence_needed": ["evidencias no automatizables"],
  "notes": "observaciones relevantes"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        return json.loads(response.content[0].text)

    def _log_agent_decision(self, **kwargs) -> None:
        """Registra cada decisión del agente para trazabilidad."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "compliance-gap-analyzer",
            **kwargs,
        }
        log_path = Path("logs/agent-decisions.jsonl")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
