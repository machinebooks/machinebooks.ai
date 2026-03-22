# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
    def generate_finding(
        self, control: AuditControl, finding_number: int
    ) -> AuditFinding:
        """Genera un hallazgo formal a partir de un control no conforme."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=f"""Eres un auditor senior redactando hallazgos
para un informe de auditoría {self.framework}.

El hallazgo debe ser:
- Objetivo: basado en hechos documentados, no opiniones
- Accionable: la recomendación debe ser implementable
- Proporcional: la severidad debe reflejar el riesgo real
- Verificable: cualquier auditor puede confirmar el hallazgo

Severidades:
- alta: riesgo de incidente grave o incumplimiento legal
- media: debilidad que incrementa la superficie de riesgo
- baja: mejora recomendable sin riesgo inmediato
- observación: oportunidad de mejora sin riesgo asociado""",
            messages=[{
                "role": "user",
                "content": f"""Control: {control.control_id} — {control.title}
Estado: {control.status}
Justificación: {control.justification}
Evidencias revisadas: {', '.join(control.evidence_refs)}

Genera el hallazgo en JSON:
{{
  "severity": "alta|media|baja|observación",
  "title": "título conciso del hallazgo",
  "description": "descripción detallada del incumplimiento",
  "evidence_quote": "cita textual de la evidencia (o ausencia)",
  "risk": "riesgo concreto si no se remedia",
  "recommendation": "acción específica de remediación",
  "estimated_effort": "esfuerzo estimado de remediación"
}}"""
            }]
        )

        result = json.loads(response.content[0].text)
        return AuditFinding(
            finding_id=f"HAL-{finding_number:03d}",
            control_id=control.control_id,
            severity=result["severity"],
            title=result["title"],
            description=result["description"],
            evidence_quote=result["evidence_quote"],
            risk=result["risk"],
            recommendation=result["recommendation"]
        )

    def run_audit(self):
        """Ejecuta la auditoría completa."""
        # Fase 1: Evaluar todos los controles
        for control in self.controls:
            self.evaluate_control(control)

        # Fase 2: Generar hallazgos para no conformidades
        finding_num = 1
        for control in self.controls:
            if control.status in ("no_cumple", "parcial"):
                finding = self.generate_finding(control, finding_num)
                self.findings.append(finding)
                finding_num += 1

        # Fase 3: Estadísticas de cumplimiento
        stats = self._calculate_stats()
        print(f"\nResultados de auditoría {self.framework}:")
        print(f"  Controles evaluados: {stats['total']}")
        print(f"  Cumplen: {stats['cumple']} ({stats['pct_cumple']:.0f}%)")
        print(f"  Parcial: {stats['parcial']} ({stats['pct_parcial']:.0f}%)")
        print(f"  No cumplen: {stats['no_cumple']} ({stats['pct_no']:.0f}%)")
        print(f"  Hallazgos generados: {len(self.findings)}")

        return self.findings
