# Extraído de: LibroCISO/cap-12-agentes-especializados.md
class ComplianceAgent(BaseAgent):
    """Agente de cumplimiento normativo.

    Ejecuta gap analysis, calcula porcentajes de cumplimiento
    y genera Declaraciones de Aplicabilidad (SoA).
    """

    TOOLS = [
        "evaluate_control_gap",
        "search_rag"
    ]

    def gather_data(self, params: dict) -> dict:
        """Consulta marcos, controles y evidencias."""
        framework_id = params["framework_id"]

        # Obtener marco con controles y evidencias
        framework = self.db_session.query(Framework)\
            .options(
                joinedload(Framework.controls)
                .joinedload(Control.evidences)
            )\
            .filter_by(id=framework_id).first()

        # Evaluar gaps
        gaps = self.tools.evaluate_control_gap(
            framework_id=framework_id
        )

        # Calcular estadísticas de cumplimiento
        total_controls = len(framework.controls)
        controls_with_evidence = sum(
            1 for c in framework.controls
            if any(e.status == "valid" for e in c.evidences)
        )

        return {
            "framework": framework.to_dict(),
            "gaps": gaps,
            "stats": {
                "total_controls": total_controls,
                "with_evidence": controls_with_evidence,
                "compliance_pct": round(
                    controls_with_evidence / total_controls * 100, 1
                ) if total_controls > 0 else 0
            }
        }

    def analyze(self, gathered: dict, params: dict) -> dict:
        """Analiza gaps y genera recomendaciones de cumplimiento."""
        fw_name = gathered["framework"]["name"]
        stats = gathered["stats"]

        # Buscar contexto normativo para los gaps detectados
        rag_context = self.tools.search_rag(
            query=f"requisitos cumplimiento {fw_name} "
                  f"controles evidencias auditoría",
            collection="normativa_compliance",
            top_k=6
        )

        system_prompt = (
            f"Eres un auditor de cumplimiento experto en {fw_name}. "
            f"El marco tiene {stats['total_controls']} controles, "
            f"de los cuales {stats['with_evidence']} tienen evidencia "
            f"válida ({stats['compliance_pct']}% de cumplimiento).\n\n"
            "Analiza los gaps identificados y genera:\n"
            "1. Priorización de controles sin evidencia por criticidad\n"
            "2. Recomendaciones concretas para cerrar cada gap\n"
            "3. Estimación de esfuerzo (horas) por gap\n"
            "4. Identificación de quick wins (gaps fáciles de cerrar)"
        )

        response = self.llm_service.invoke(
            model="claude-sonnet-4-6",
            system=system_prompt,
            messages=[{"role": "user", "content":
                      self._build_compliance_prompt(gathered, rag_context)}],
            max_tokens=4096,
            temperature=0.2
        )

        self.total_tokens += response.usage.total_tokens
        self.total_cost += response.cost

        return {
            "gap_analysis": response.content,
            "stats": stats,
            "model_used": response.model,
            "tokens": response.usage.total_tokens
        }
