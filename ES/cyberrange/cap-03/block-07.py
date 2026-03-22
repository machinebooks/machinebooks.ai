# Extraído de: LibroCyberrange/cap-03-arquitecto-cyber-range.md
# Métricas del arquitecto
# Ejemplo didáctico: patrones/metrics/architect.py

ARCHITECT_METRICS = {
    # Calidad de código
    "code_coverage": {
        "target": ">80%",
        "current": "83%",
        "note": "Tests funcionales + adversariales"
    },
    "security_findings_per_sprint": {
        "target": "<5 high/critical",
        "current": "2-3 por sprint",
        "note": "Tendencia descendente desde que se añadieron "
                "reglas de seguridad al CLAUDE.md"
    },

    # Calidad de IA
    "ai_hallucination_rate": {
        "target": "<10%",
        "current": "~7%",
        "note": "Porcentaje de generaciones que contienen errores "
                "factuales verificables (IPs incorrectas, paths "
                "inexistentes, configuraciones inválidas)"
    },
    "ai_security_issues_rate": {
        "target": "<15%",
        "current": "~12%",
        "note": "Porcentaje de generaciones que contienen al menos "
                "un hallazgo de seguridad en la revisión"
    },

    # Operaciones
    "deployment_success_rate": {
        "target": ">95%",
        "current": "97%",
        "note": "Porcentaje de escenarios que se despliegan "
                "correctamente en el primer intento"
    },
    "scenario_generation_time": {
        "target": "<15 min",
        "current": "8-12 min",
        "note": "Desde la descripción hasta el escenario validado "
                "y listo para despliegue (incluye revisión humana)"
    },

    # Eficiencia del ciclo arquitecto-Claude
    "code_accepted_first_review": {
        "target": ">70%",
        "current": "74%",
        "note": "Código generado por Claude que pasa la revisión "
                "del arquitecto sin correcciones mayores"
    },
}
