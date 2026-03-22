# Extraído de: LibroFinOps/cap-26-caso-cloud.md
# services/optimization_pipeline.py
# Pipeline que garantiza que ninguna acción destructiva
# se ejecuta sin supervisión humana.

class OptimizationPipeline:
    """
    Orquesta el flujo completo: detección → aprobación → ejecución.

    Estados: DETECTADA → PROPUESTA → (APROBADA | RECHAZADA) →
             (DRY_RUN) → EJECUTADA
    """

    def __init__(self):
        self.agent = CloudOptimizerAgent()
        self.client = anthropic.Anthropic()

    def ejecutar_ciclo_semanal(self) -> dict:
        """
        1. Escaneo y análisis (agente autónomo)
        2. Clasificación por nivel de riesgo
        3. Ejecución automática de bajo riesgo
        4. Envío para aprobación de medio y alto riesgo
        """
        recomendaciones = self.agent.ejecutar_analisis_completo()

        if not recomendaciones:
            return {"estado": "sin_recomendaciones"}

        # Clasificar por nivel de riesgo
        automaticas = [
            r for r in recomendaciones
            if r.nivel_riesgo == NivelRiesgo.BAJO
        ]
        requieren_aprobacion = [
            r for r in recomendaciones
            if r.nivel_riesgo != NivelRiesgo.BAJO
        ]

        # Ejecutar automáticamente las de bajo riesgo
        ejecutadas = []
        for rec in automaticas:
            resultado = self._ejecutar_accion_automatica(rec)
            ejecutadas.append({"id": rec.id, "resultado": resultado})

        # Generar solicitud de aprobación para el resto
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
