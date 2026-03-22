# Extraído de: LibroDevSecOps/cap-04-sast-inteligente.md
COLUMNAS_VALIDAS = {"nombre", "email", "departamento"}

def ordenar_resultados(columna):
    if columna not in COLUMNAS_VALIDAS:
        columna = "nombre"
    query = f"SELECT * FROM usuarios ORDER BY {columna}"
    cursor.execute(query)
