# Extraído de: LibroTecnico/cap-24-documentacion-ia.md
import anthropic
import ast
import inspect
from pathlib import Path

def extraer_contexto_blueprint(ruta_blueprint: str) -> dict:
    """
    Extrae la información estructurada de un blueprint Flask
    para usarla como contexto en la generación de documentación.
    """
    codigo = Path(ruta_blueprint).read_text(encoding="utf-8")

    # Extraer rutas, métodos HTTP, decoradores de autenticación y docstrings
    contexto = {
        "rutas": [],
        "modelos_entrada": [],
        "modelos_salida": [],
        "middleware": [],
        "descripcion_modulo": ""
    }

    # Parsear el AST para extraer información estructurada
    arbol = ast.parse(codigo)
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef):
            docstring = ast.get_docstring(nodo)
            decoradores = [ast.unparse(d) for d in nodo.decorator_list]
            if any("route" in d for d in decoradores):
                contexto["rutas"].append({
                    "funcion": nodo.name,
                    "decoradores": decoradores,
                    "docstring": docstring or "",
                    "linea": nodo.lineno
                })

    return contexto


def generar_documentacion_modulo(
    ruta_blueprint: str,
    modulo_nombre: str
) -> str:
    """
    Genera documentación completa de un módulo API usando Claude.
    """
    client = anthropic.Anthropic()
    contexto = extraer_contexto_blueprint(ruta_blueprint)

    prompt = f"""Genera documentación técnica completa para el módulo de API '{modulo_nombre}'.

Contexto del módulo:
{contexto}

La documentación debe incluir:
1. Descripción general del módulo y su propósito
2. Tabla de endpoints con método HTTP, ruta, autenticación requerida y descripción
3. Para cada endpoint principal: parámetros, cuerpo de petición y estructura de respuesta
4. Ejemplos de uso con curl
5. Códigos de error específicos del módulo

Formato: Markdown. Nivel técnico: desarrollador que va a integrar contra la API.
No incluir información interna sobre la implementación ni rutas de fichero del servidor."""

    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return mensaje.content[0].text
