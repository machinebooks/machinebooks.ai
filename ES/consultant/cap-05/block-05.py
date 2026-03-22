# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
MAPPING_PROMPT = """Eres un agente especializado en mapeo de controles
entre frameworks de seguridad y cumplimiento. Tu trabajo es identificar
correspondencias entre controles de diferentes frameworks.

Para cada par de controles, clasifica la relación como:
- EQUIVALENTE: cubren el mismo requisito con alcance similar
- PARCIAL: se solapan pero uno es más amplio que el otro
- COMPLEMENTARIO: se refuerzan mutuamente sin solaparse
- SIN_RELACION: no tienen conexión temática

Incluye siempre la justificación de la clasificación.
"""

@tool
def get_framework_mapping(
    source_framework: str,
    source_control: str,
    target_framework: str
) -> list[dict]:
    """Obtiene el mapeo de un control de un framework a controles
    equivalentes o relacionados de otro framework.

    Args:
        source_framework: Framework de origen (iso27001, ens, dora)
        source_control: Control de origen (ej: 'A.5.1')
        target_framework: Framework de destino
    """
    conn = sqlite3.connect("framework_mappings.db")
    cursor = conn.execute("""
        SELECT target_control, relationship, justification
        FROM mappings
        WHERE source_framework = ?
          AND source_control = ?
          AND target_framework = ?
    """, (source_framework, source_control, target_framework))

    return [
        {
            "target_control": row[0],
            "relationship": row[1],
            "justification": row[2]
        }
        for row in cursor.fetchall()
    ]
