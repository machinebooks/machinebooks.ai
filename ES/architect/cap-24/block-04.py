# Extraído de: LibroTecnico/cap-24-documentacion-ia.md
import anthropic
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SeccionManual:
    titulo: str
    funcionalidades: List[str]
    flujos_usuario: List[dict]
    casos_uso_frecuentes: List[str]
    restricciones_rol: dict
    capturas_descripciones: List[str]

def construir_contexto_seccion(seccion: SeccionManual) -> str:
    """
    Construye el contexto estructurado para la generación de una sección
    del manual de usuario. La calidad del contexto determina la calidad
    del manual generado.
    """
    return f"""
## Sección: {seccion.titulo}

### Funcionalidades disponibles
{chr(10).join(f'- {f}' for f in seccion.funcionalidades)}

### Flujos de usuario documentados
{json.dumps(seccion.flujos_usuario, ensure_ascii=False, indent=2)}

### Casos de uso frecuentes identificados en producción
{chr(10).join(f'- {c}' for c in seccion.casos_uso_frecuentes)}

### Control de acceso por rol
{json.dumps(seccion.restricciones_rol, ensure_ascii=False, indent=2)}

### Descripciones de pantallas
{chr(10).join(seccion.capturas_descripciones)}
"""

def generar_seccion_manual(
    seccion: SeccionManual,
    tono: str = "profesional-accesible"
) -> str:
    """
    Genera una sección completa del manual de usuario.
    Cada sección se genera independientemente para gestionar el contexto.
    """
    client = anthropic.Anthropic()
    contexto = construir_contexto_seccion(seccion)

    prompt = f"""Genera la sección '{seccion.titulo}' de un manual de usuario para
una plataforma de análisis de negocio B2B.

Contexto del módulo:
{contexto}

Instrucciones de redacción:
- Tono: {tono} — claro, sin jerga técnica innecesaria
- Estructura: descripción general, guía paso a paso, casos de uso, preguntas frecuentes
- Incluir notas de advertencia donde el usuario pueda cometer errores comunes
- No mencionar nombres de ficheros, rutas de servidor ni detalles de implementación
- Usar "la Plataforma" para referirse al sistema, nunca nombres propietarios
- Formato: Markdown con encabezados h2 y h3, listas y tablas donde aporten claridad

El manual debe ser útil para un analista de negocio con experiencia media en herramientas
digitales, no para un desarrollador."""

    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return mensaje.content[0].text


def ensamblar_manual_completo(
    secciones: List[SeccionManual],
    output_path: str
) -> None:
    """
    Genera todas las secciones y ensambla el manual completo.
    Añade portada, tabla de contenidos y sección de glosario.
    """
    partes = []
    partes.append(generar_portada())

    for seccion in secciones:
        print(f"Generando sección: {seccion.titulo}...")
        contenido = generar_seccion_manual(seccion)
        partes.append(contenido)

    partes.append(generar_glosario(secciones))

    manual_completo = "\n\n---\n\n".join(partes)
    Path(output_path).write_text(manual_completo, encoding="utf-8")
    print(f"Manual generado: {output_path}")
