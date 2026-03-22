# Extraído de: LibroDevSecOps/cap-04-sast-inteligente.md
def buscar_usuario(nombre):
    query = f"SELECT * FROM usuarios WHERE nombre = '{nombre}'"
    cursor.execute(query)
