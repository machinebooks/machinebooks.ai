# Extraído de: LibroDevSecOps/cap-28-caso-compliance.md
# Extensión de la matriz de mapeo para AI Act
AIACT_CONTROL_MAP = {
    "art.11": {
        "nombre": "Documentación técnica",
        "artefactos_requeridos": [
            "ai-system-documentation.json",
            "model-inventory.json"
        ],
        "criterio": "Documentación actualizada de cada sistema de IA"
    },
    "art.12": {
        "nombre": "Conservación de registros",
        "artefactos_requeridos": [
            "llm-usage-logs.json"
        ],
        "criterio": "Logs de input/output de cada llamada LLM"
    },
    "art.14": {
        "nombre": "Supervisión humana",
        "artefactos_requeridos": [
            "human-oversight-config.json",
            "escalation-log.json"
        ],
        "criterio": "Mecanismo de supervisión humana documentado y activo"
    },
    "art.15": {
        "nombre": "Precisión, solidez y ciberseguridad",
        "artefactos_requeridos": [
            "adversarial-test-results.sarif",
            "prompt-injection-report.json"
        ],
        "criterio": "Tests adversariales ejecutados, sin vulnerabilidades críticas"
    },
}

# El mismo agente evalúa ambas matrices
def ejecutar_compliance_dual(bucket_path: str):
    """Evalúa compliance ENS y AI Act con el mismo sistema."""
    client = anthropic.Anthropic()
    evidencias = recopilar_evidencias(bucket_path)

    resultados_ens = {}
    for cid, cdef in ENS_CONTROL_MAP.items():
        resultados_ens[cid] = evaluar_control(
            cid, cdef, evidencias, client
        )

    resultados_aiact = {}
    for cid, cdef in AIACT_CONTROL_MAP.items():
        resultados_aiact[cid] = evaluar_control(
            cid, cdef, evidencias, client
        )

    # Generar informe unificado
    informe = generar_informe_dual(
        resultados_ens, resultados_aiact, client
    )
    return informe
