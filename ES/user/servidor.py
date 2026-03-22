# Extraído de: LibroUsuario/cap-10-construir-tu-conector-mcp.md
# servidor.py — Servidor MCP para consultar el sistema de gestión
# Este servidor expone herramientas para que Claude pueda consultar
# información de clientes y pedidos.

from mcp.server.fastmcp import FastMCP
import httpx
import json

# Crear el servidor MCP con un nombre descriptivo.
# Este nombre es el que verás en Claude Desktop.
servidor = FastMCP("gestion-empresa")

# URL base de la API a la que te conectas.
# En un caso real, pon aquí la URL de tu API interna.
# Ejemplo: "https://api.interna.tuempresa.com/v1"
API_BASE = "https://api.ejemplo.com/v1"

# Token de autenticación para la API.
# En un caso real, usa una variable de entorno (más seguro)
# en lugar de escribir el token directamente en el código.
import os
API_TOKEN = os.environ.get("API_TOKEN", "tu-token-aqui")

# Cabeceras que se envían con cada petición a la API.
# La mayoría de APIs requieren un token de autenticación
# y que indiques que esperas recibir datos en formato JSON.
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


# --- HERRAMIENTA 1: Buscar clientes ---
# El decorador @servidor.tool() le dice a MCP que esta función
# es una herramienta que Claude puede usar.
# La descripción es lo que Claude lee para saber cuándo usar esta herramienta.

@servidor.tool()
async def buscar_cliente(nombre: str) -> str:
    """
    Busca clientes en el sistema de gestión por nombre.
    Devuelve una lista de clientes que coinciden con el nombre buscado,
    incluyendo su ID, nombre completo, email y ciudad.
    """
    # Hacemos una petición GET a la API con el nombre como parámetro.
    # 'async with' abre una conexión HTTP que se cierra automáticamente.
    async with httpx.AsyncClient() as client:
        respuesta = await client.get(
            f"{API_BASE}/clientes",
            params={"buscar": nombre},
            headers=HEADERS
        )

    # Si la API responde con un error, informamos a Claude.
    if respuesta.status_code != 200:
        return f"Error al buscar clientes: código {respuesta.status_code}"

    # Convertimos la respuesta JSON en texto legible.
    clientes = respuesta.json()

    if not clientes:
        return f"No se encontraron clientes con el nombre '{nombre}'."

    # Formateamos los resultados para que Claude los entienda fácilmente.
    resultado = f"Se encontraron {len(clientes)} cliente(s):\n\n"
    for c in clientes:
        resultado += f"- ID: {c['id']}\n"
        resultado += f"  Nombre: {c['nombre']}\n"
        resultado += f"  Email: {c['email']}\n"
        resultado += f"  Ciudad: {c['ciudad']}\n\n"

    return resultado


# --- HERRAMIENTA 2: Consultar pedidos de un cliente ---

@servidor.tool()
async def pedidos_cliente(cliente_id: int) -> str:
    """
    Consulta los pedidos de un cliente específico usando su ID.
    Devuelve la lista de pedidos con fecha, importe y estado
    (pendiente, enviado, entregado).
    """
    async with httpx.AsyncClient() as client:
        respuesta = await client.get(
            f"{API_BASE}/clientes/{cliente_id}/pedidos",
            headers=HEADERS
        )

    if respuesta.status_code != 200:
        return f"Error al consultar pedidos: código {respuesta.status_code}"

    pedidos = respuesta.json()

    if not pedidos:
        return f"El cliente {cliente_id} no tiene pedidos registrados."

    resultado = f"Pedidos del cliente {cliente_id}:\n\n"
    total = 0
    for p in pedidos:
        resultado += f"- Pedido #{p['id']}\n"
        resultado += f"  Fecha: {p['fecha']}\n"
        resultado += f"  Importe: {p['importe']:.2f} EUR\n"
        resultado += f"  Estado: {p['estado']}\n\n"
        total += p['importe']

    resultado += f"Total acumulado: {total:.2f} EUR"
    return resultado


# --- HERRAMIENTA 3: Resumen de ventas del mes ---

@servidor.tool()
async def resumen_ventas(mes: int, anio: int) -> str:
    """
    Obtiene un resumen de ventas del mes indicado.
    Incluye total de pedidos, importe total, pedido medio
    y los 5 clientes con mayor volumen de compra.
    Parámetros: mes (1-12) y anio (por ejemplo, 2025).
    """
    async with httpx.AsyncClient() as client:
        respuesta = await client.get(
            f"{API_BASE}/ventas/resumen",
            params={"mes": mes, "anio": anio},
            headers=HEADERS
        )

    if respuesta.status_code != 200:
        return f"Error al obtener resumen de ventas: código {respuesta.status_code}"

    datos = respuesta.json()

    resultado = f"Resumen de ventas — {mes:02d}/{anio}\n"
    resultado += "=" * 40 + "\n\n"
    resultado += f"Total de pedidos: {datos['total_pedidos']}\n"
    resultado += f"Importe total: {datos['importe_total']:.2f} EUR\n"
    resultado += f"Pedido medio: {datos['pedido_medio']:.2f} EUR\n\n"
    resultado += "Top 5 clientes:\n"
    for i, c in enumerate(datos.get('top_clientes', []), 1):
        resultado += f"  {i}. {c['nombre']} — {c['importe']:.2f} EUR\n"

    return resultado


# --- Punto de entrada del servidor ---
# Esta línea hace que el servidor arranque cuando se ejecuta el archivo.
if __name__ == "__main__":
    servidor.run(transport="stdio")
