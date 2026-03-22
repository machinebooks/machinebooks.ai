# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
@tool
def store_finding(
    framework_ref: str,
    status: str,
    evidencia: str,
    gap: str,
    riesgo: str,
    recomendacion: str,
    confianza: float,
    source_docs: list[str] | None = None
) -> dict:
    """Almacena un hallazgo de análisis en la base de datos del proyecto.

    Args:
        framework_ref: Referencia al control evaluado
        status: conforme | parcial | no_conforme | no_aplica
        evidencia: Resumen de evidencia analizada
        gap: Descripción de la discrepancia
        riesgo: crítico | alto | medio | bajo
        recomendacion: Acción concreta para cerrar el gap
        confianza: Nivel de confianza (0.0 a 1.0)
        source_docs: Lista de documentos fuente consultados
    """
    # Validación de campos
    valid_status = {"conforme", "parcial", "no_conforme", "no_aplica"}
    valid_riesgo = {"crítico", "alto", "medio", "bajo"}

    if status not in valid_status:
        return {"error": f"Estado inválido: {status}. Usar: {valid_status}"}
    if riesgo not in valid_riesgo:
        return {"error": f"Riesgo inválido: {riesgo}. Usar: {valid_riesgo}"}
    if not 0.0 <= confianza <= 1.0:
        return {"error": "Confianza debe estar entre 0.0 y 1.0"}

    conn = sqlite3.connect("findings.db")
    conn.execute("""
        INSERT INTO findings
        (framework_ref, status, evidencia, gap, riesgo,
         recomendacion, confianza, source_docs, fecha_analisis,
         client_id, project_id, reviewed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, 0)
    """, (
        framework_ref, status, evidencia, gap, riesgo,
        recomendacion, confianza,
        json.dumps(source_docs or []),
        # client_id y project_id del contexto del agente
        "CURRENT_CLIENT", "CURRENT_PROJECT"
    ))
    conn.commit()

    return {
        "stored": True,
        "framework_ref": framework_ref,
        "status": status,
        "requires_review": confianza < 0.5
    }
