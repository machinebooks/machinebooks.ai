# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
import sqlite3

@tool
def query_previous_findings(
    client_id: str,
    framework: str | None = None,
    control_ref: str | None = None
) -> list[dict]:
    """Consulta hallazgos de análisis anteriores para un cliente.
    Útil para identificar recurrencias y evaluar evolución.

    Args:
        client_id: Identificador del cliente
        framework: Filtrar por framework específico
        control_ref: Filtrar por control específico
    """
    conn = sqlite3.connect("findings.db")
    query = """
        SELECT framework_ref, status, gap, riesgo,
               recomendacion, fecha_analisis, proyecto
        FROM findings
        WHERE client_id = ?
    """
    params = [client_id]

    if framework:
        query += " AND framework = ?"
        params.append(framework)
    if control_ref:
        query += " AND framework_ref = ?"
        params.append(control_ref)

    query += " ORDER BY fecha_analisis DESC LIMIT 20"
    cursor = conn.execute(query, params)
    columns = [d[0] for d in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
