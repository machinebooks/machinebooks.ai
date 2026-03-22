# Extraído de: LibroUsuario/cap-10-construir-tu-conector-mcp.md
# servidor_bd.py — Servidor MCP para consultar una base de datos SQLite
from mcp.server.fastmcp import FastMCP
import sqlite3
import os

servidor = FastMCP("base-datos-empresa")

# Ruta al archivo de base de datos
DB_PATH = os.environ.get("DB_PATH", "empresa.db")


@servidor.tool()
async def consultar(pregunta: str) -> str:
    """
    Ejecuta una consulta SQL de solo lectura en la base de datos
    de la empresa. Acepta consultas SELECT para buscar información
    sobre clientes, pedidos, productos e inventario.
    IMPORTANTE: Solo se permiten consultas de lectura (SELECT).
    No se pueden modificar datos.
    """
    # Verificar que la consulta es de solo lectura (medida de seguridad)
    pregunta_limpia = pregunta.strip().upper()
    if not pregunta_limpia.startswith("SELECT"):
        return "Error: Solo se permiten consultas de lectura (SELECT)."

    # Palabras peligrosas que no deberían aparecer en una consulta de lectura
    palabras_prohibidas = ["DROP", "DELETE", "UPDATE", "INSERT",
                          "ALTER", "CREATE", "TRUNCATE"]
    for palabra in palabras_prohibidas:
        if palabra in pregunta_limpia:
            return f"Error: La consulta contiene una operación no permitida ({palabra})."

    try:
        # Conectar a la base de datos en modo solo lectura
        conexion = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conexion.cursor()

        # Ejecutar la consulta
        cursor.execute(pregunta)
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        conexion.close()

        if not filas:
            return "La consulta no devolvió resultados."

        # Formatear como tabla legible
        resultado = "Columnas: " + " | ".join(columnas) + "\n"
        resultado += "-" * 60 + "\n"
        for fila in filas[:100]:  # Limitar a 100 filas por seguridad
            resultado += " | ".join(str(v) for v in fila) + "\n"

        if len(filas) > 100:
            resultado += f"\n(Mostrando 100 de {len(filas)} resultados)"

        return resultado

    except Exception as e:
        return f"Error al ejecutar la consulta: {str(e)}"


@servidor.tool()
async def listar_tablas() -> str:
    """
    Lista todas las tablas disponibles en la base de datos
    con sus columnas. Útil para saber qué datos se pueden consultar.
    """
    try:
        conexion = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conexion.cursor()

        # Obtener la lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [fila[0] for fila in cursor.fetchall()]

        resultado = "Tablas disponibles:\n\n"
        for tabla in tablas:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = cursor.fetchall()
            resultado += f"  {tabla}:\n"
            for col in columnas:
                resultado += f"    - {col[1]} ({col[2]})\n"
            resultado += "\n"

        conexion.close()
        return resultado

    except Exception as e:
        return f"Error al listar tablas: {str(e)}"


if __name__ == "__main__":
    servidor.run(transport="stdio")
