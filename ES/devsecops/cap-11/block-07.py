# Extraído de: LibroDevSecOps/cap-11-remediacion-automatica.md
# ANTES (vulnerable a SQL injection — CWE-89)
def get_report(cursor, report_id: str) -> dict:
    query = f"SELECT * FROM reports WHERE id = {report_id}"
    cursor.execute(query)
    return cursor.fetchone()

# DESPUÉS (parameterized query — fix del agente)
def get_report(cursor, report_id: str) -> dict:
    query = "SELECT * FROM reports WHERE id = %s"
    cursor.execute(query, (report_id,))
    return cursor.fetchone()
