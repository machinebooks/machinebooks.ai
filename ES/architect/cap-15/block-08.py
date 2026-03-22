# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
import anthropic
import sqlparse
from typing import Optional

ALLOWED_TABLES = {
    "opportunities", "proposals", "clients",
    "pipeline_stages", "revenue_entries"
}

ANALYTICS_SCHEMA_CONTEXT = """
Tablas disponibles (solo lectura):
- opportunities(id, title, value_eur, stage, created_at, closed_at, client_id)
- proposals(id, opportunity_id, type, status, created_at, submitted_at)
- clients(id, name, sector, tier, account_manager)
- pipeline_stages(id, name, order_num, conversion_rate_avg)
- revenue_entries(id, client_id, amount_eur, period, type)
"""

async def generate_analytics_query(
    user_question: str,
    client: anthropic.Anthropic
) -> Optional[str]:
    """
    Genera SQL seguro a partir de una pregunta en lenguaje natural.
    Incluye validación antes de devolver la consulta.
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=f"""Eres un generador de SQL para analytics.
        {ANALYTICS_SCHEMA_CONTEXT}

        Reglas:
        - Genera SOLO SELECT. Nunca INSERT, UPDATE, DELETE, DROP.
        - Usa solo las tablas de la lista.
        - Añade LIMIT 1000 si no hay LIMIT explícito.
        - Devuelve SOLO el SQL, sin explicaciones.""",
        messages=[{"role": "user", "content": user_question}]
    )

    sql = response.content[0].text.strip()

    # Validar que el SQL es un SELECT y solo accede a tablas permitidas
    if not validate_analytics_sql(sql):
        return None

    return sql

def validate_analytics_sql(sql: str) -> bool:
    """
    Validación básica de seguridad: solo SELECT, solo tablas permitidas.
    No es un sustituto de una capa de BD de solo lectura.
    """
    parsed = sqlparse.parse(sql)
    if not parsed:
        return False

    stmt = parsed[0]
    stmt_type = stmt.get_type()

    # Solo SELECT permitido
    if stmt_type != 'SELECT':
        return False

    # Verificar que no hay tablas fuera de la lista blanca
    # (implementación simplificada, producción usa un parser más robusto)
    sql_lower = sql.lower()
    for token in stmt.flatten():
        if token.ttype is sqlparse.tokens.Name:
            if token.value.lower() not in ALLOWED_TABLES and \
               token.value.lower() not in {'id', 'and', 'or', 'not', 'in', 'is', 'null'}:
                # Comprobación heurística: si parece un nombre de tabla no permitida
                if any(keyword in sql_lower for keyword in ['from', 'join']):
                    return False

    return True
