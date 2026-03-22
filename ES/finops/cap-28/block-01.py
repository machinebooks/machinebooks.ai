# Extraído de: LibroFinOps/cap-28-finops-agentes-autonomos.md
    def generar_contexto_para_agente(self) -> str:
        """
        Genera el contexto de presupuesto que se inyecta en el prompt.
        El agente lee este contexto para tomar decisiones adaptativas.
        """
        estado = "normal"
        instruccion = ""

        if self.debe_detenerse:
            estado = "CRÍTICO"
            instruccion = (
                "DETENER y entregar resultado parcial con explicación."
            )
        elif self.debe_escalar:
            estado = "BAJO"
            instruccion = (
                "Simplificar al máximo. Entregar solo el resultado esencial."
            )
        elif self.debe_simplificar:
            estado = "AJUSTADO"
            instruccion = (
                "Optimizar eficiencia. Evitar llamadas innecesarias."
            )

        return f"""[CONTEXTO FINANCIERO DEL WORKFLOW]
Presupuesto total: €{self.presupuesto_total_eur:.4f}
Presupuesto restante: €{self.presupuesto_restante_eur:.4f} ({self.pct_presupuesto_restante*100:.1f}%)
Estado: {estado}
Llamadas LLM realizadas: {self.num_llamadas_llm}
Tiempo transcurrido: {self.tiempo_transcurrido_segundos:.0f}s / {self.tiempo_limite_segundos}s
{"INSTRUCCIÓN: " + instruccion if instruccion else ""}"""
