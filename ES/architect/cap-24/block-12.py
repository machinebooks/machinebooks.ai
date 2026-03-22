# Extraído de: LibroTecnico/cap-24-documentacion-ia.md
# Ejemplo de validación automática de referencias de API
def validar_rutas_documentadas(
    doc_path: str,
    codigo_backend_path: str
) -> List[dict]:
    """
    Extrae rutas de API mencionadas en la documentación y verifica
    que existen en el código del backend.
    Devuelve una lista de divergencias para revisión.
    """
    rutas_documentadas = extraer_rutas_de_markdown(doc_path)
    rutas_codigo = extraer_rutas_de_flask(codigo_backend_path)

    divergencias = []
    for ruta in rutas_documentadas:
        if ruta["path"] not in rutas_codigo:
            divergencias.append({
                "tipo": "ruta_documentada_no_existe",
                "ruta": ruta["path"],
                "metodo": ruta["method"],
                "linea_doc": ruta["linea"],
                "accion_requerida": "eliminar_de_docs_o_re-implementar"
            })

    for ruta in rutas_codigo:
        if ruta not in [r["path"] for r in rutas_documentadas]:
            divergencias.append({
                "tipo": "ruta_sin_documentar",
                "ruta": ruta,
                "accion_requerida": "documentar_o_marcar_como_interno"
            })

    return divergencias
