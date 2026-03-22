# Source: The FinOps Engineer and the Machine -- Chapter 26
# Pattern: Full cloud optimization agent

# services/optimization_pipeline.py
# Pipeline that ensures no destructive action
# is executed without human supervision.

class OptimizationPipeline:
    """
    Orchestrates the full flow: detection → approval → execution.

    Estados: DETECTADA → PROPUESTA → (APROBADA | RECHAZADA) →
             (DRY_RUN) → EJECUTADA
    """

    def __init__(self):
        self.agent = CloudOptimizerAgent()
        self.client = anthropic.Anthropic()

    def ejecutar_ciclo_semanal(self) -> dict:
        """
        1. Scanning and analysis (autonomous agent)
        2. Classification by risk level
        3. Automatic execution of low-risk items
        4. Submission for approval of medium and high-risk items
        """
        recomendaciones = self.agent.ejecutar_analisis_completo()

        if not recomendaciones:
            return {"estado": "sin_recomendaciones"}

        # Classify by risk level
        automaticas = [
            r for r in recomendaciones
            if r.nivel_riesgo == NivelRiesgo.BAJO
        ]
        requieren_aprobacion = [
            r for r in recomendaciones
            if r.nivel_riesgo != NivelRiesgo.BAJO
        ]

        # Automatically execute low-risk items
        ejecutadas = []
        for rec in automaticas:
            resultado = self._ejecutar_accion_automatica(rec)
            ejecutadas.append({"id": rec.id, "resultado": resultado})

        # Generate approval request for the rest
        if requieren_aprobacion:
            self._enviar_solicitud_aprobacion(requieren_aprobacion)

        return {
            "estado": "completado",
            "timestamp": datetime.utcnow(),
            "total": len(recomendaciones),
            "ejecutadas_auto": len(ejecutadas),
            "pendientes": len(requieren_aprobacion),
            "ahorro_auto_anual_usd": sum(
                r.ahorro_anual_est_usd for r in automaticas
            ),
            "ahorro_pendiente_usd": sum(
                r.ahorro_anual_est_usd for r in requieren_aprobacion
            ),
        }
