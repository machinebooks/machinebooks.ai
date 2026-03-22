# Extraído de: LibroConsultor/cap-09-generacion-propuestas.md
from typing import Generator

# Orden de generación (el resumen ejecutivo va al final)
ORDEN_GENERACION = [
    SeccionTipo.COMPRENSION_NECESIDAD,
    SeccionTipo.ENFOQUE_TECNICO,
    SeccionTipo.METODOLOGIA,
    SeccionTipo.PLAN_TRABAJO,
    SeccionTipo.EQUIPO,
    SeccionTipo.RESUMEN_EJECUTIVO,
]

def generar_propuesta(
    contexto: ContextoPropuesta,
    umbral_quality: float = 70.0,
    max_reintentos: int = 2
) -> Generator[SeccionGenerada, None, None]:
    """Pipeline completo de generación de propuesta.

    Genera secciones en orden, evaluando cada una.
    Si el score está por debajo del umbral, regenera con feedback.
    Devuelve secciones para revisión humana incremental.
    """
    secciones_generadas: dict[SeccionTipo, str] = {}
    coste_total = 0.0

    for tipo_seccion in ORDEN_GENERACION:
        # 1. Recuperar secciones de referencia via RAG
        referencias = recuperar_secciones_similares(
            tipo_seccion=tipo_seccion,
            sector=contexto.sector,
            tipo_servicio=contexto.tipo_servicio,
            descripcion_necesidad=contexto.requisitos_pliego[0].get(
                "descripcion", ""
            )
        )

        # 2. Identificar criterio de valoración relevante
        criterio = next(
            (c for c in contexto.criterios_valoracion
             if tipo_seccion.value in c.get("secciones_relacionadas", [])),
            contexto.criterios_valoracion[0]  # Fallback
        )

        # 3. Generar sección con contexto
        seccion = generar_seccion(
            tipo=tipo_seccion,
            contexto=contexto,
            secciones_referencia=referencias,
            secciones_previas=secciones_generadas
        )

        # 4. Quality gate
        evaluacion = evaluar_seccion(seccion, contexto, criterio)

        # 5. Regenerar si no alcanza el umbral
        intentos = 0
        while seccion.score_quality < umbral_quality and intentos < max_reintentos:
            seccion.notas_revision.append(
                f"Regeneración automática — carencias: "
                f"{', '.join(evaluacion['carencias'][:3])}"
            )
            seccion = generar_seccion(
                tipo=tipo_seccion,
                contexto=contexto,
                secciones_referencia=referencias,
                secciones_previas=secciones_generadas
            )
            seccion.version += intentos + 1
            evaluacion = evaluar_seccion(seccion, contexto, criterio)
            intentos += 1

        coste_total += seccion.coste_generacion
        secciones_generadas[tipo_seccion] = seccion.contenido

        # Devolver para revisión humana incremental
        yield seccion

    print(f"Propuesta generada — coste total: ${coste_total:.2f}")
