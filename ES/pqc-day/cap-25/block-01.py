# Extraído de: LibroPQC/cap-25-mercado.md
from datetime import datetime, timedelta
from typing import Optional


class ComplianceReportGenerator:
    """Genera informes de cumplimiento regulatorio PQC por framework."""

    def __init__(self, organization_id: int, framework_id: str):
        self.organization_id = organization_id
        self.framework = REGULATORY_FRAMEWORKS.get(framework_id)
        self.findings = []  # Hallazgos criptográficos del cliente
        self.controls_status = {}

    def evaluate_controls(self) -> dict:
        """Evalúa el estado de cada control regulatorio
        contra los hallazgos criptográficos del cliente."""
        results = {
            "framework": self.framework["nombre_completo"],
            "fecha_evaluacion": datetime.utcnow().isoformat(),
            "organization_id": self.organization_id,
            "controles": [],
            "resumen": {
                "total": 0,
                "cumplidos": 0,
                "parciales": 0,
                "no_cumplidos": 0,
            },
        }

        for control in self.framework["controles_pqc"]:
            status = self._evaluate_single_control(control)
            results["controles"].append(status)
            results["resumen"]["total"] += 1
            results["resumen"][status["estado"]] += 1

        # Calcular puntuación global de compliance
        total = results["resumen"]["total"]
        if total > 0:
            cumplidos = results["resumen"]["cumplidos"]
            parciales = results["resumen"]["parciales"]
            results["puntuacion"] = round(
                ((cumplidos * 1.0 + parciales * 0.5) / total) * 100, 1
            )

        return results

    def _evaluate_single_control(self, control: dict) -> dict:
        """Evalúa un control individual contra los hallazgos."""
        # Obtener hallazgos relevantes para el módulo del control
        relevant = [
            f for f in self.findings
            if f.get("modulo") == control["modulo_plataforma"]
        ]

        # Calcular días restantes hasta fecha límite
        deadline = datetime.fromisoformat(control["fecha_limite"])
        dias_restantes = (deadline - datetime.utcnow()).days

        # Determinar estado
        if not relevant:
            estado = "no_cumplidos"  # Sin datos = sin evaluación
            descripcion = "No se ha ejecutado la evaluación correspondiente"
        elif all(f.get("pqc_compliant") for f in relevant):
            estado = "cumplidos"
            descripcion = "Todos los hallazgos son PQC-compliant"
        elif any(f.get("pqc_compliant") for f in relevant):
            estado = "parciales"
            # Calcular porcentaje de cumplimiento
            pct = sum(1 for f in relevant if f.get("pqc_compliant"))
            descripcion = f"{pct}/{len(relevant)} hallazgos PQC-compliant"
        else:
            estado = "no_cumplidos"
            descripcion = "Ningún hallazgo es PQC-compliant"

        return {
            "control_id": control["id"],
            "descripcion_control": control["descripcion"],
            "estado": estado,
            "descripcion_estado": descripcion,
            "hallazgos_evaluados": len(relevant),
            "dias_hasta_deadline": dias_restantes,
            "urgencia": "critica" if dias_restantes < 180 else
                        "alta" if dias_restantes < 365 else "normal",
        }
