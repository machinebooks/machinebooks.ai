# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
def extraer_presupuesto(entrada) -> float:
    """
    Extrae el presupuesto de campos heterogéneos.
    Distintas fuentes usan nombres de campo diferentes.
    """
    # Intentar campos estructurados primero
    for campo in ["presupuesto_base", "valor_estimado", "importe_contrato"]:
        if hasattr(entrada, campo):
            valor = getattr(entrada, campo)
            if valor:
                return float(str(valor).replace(".", "").replace(",", ".").strip())

    # Fallback: extraer de texto libre con regex
    texto = entrada.get("summary", "") + " " + entrada.get("title", "")
    patron = r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(?:euros?|EUR|€)'
    coincidencias = re.findall(patron, texto)
    if coincidencias:
        return float(coincidencias[0].replace(".", "").replace(",", "."))

    return 0.0  # Sin presupuesto conocido — indexar igualmente


def inferir_categoria(texto: str) -> str:
    """
    Clasifica el texto en la taxonomía normalizada.
    Devuelve la primera categoría que supere el umbral de términos.
    """
    texto_lower = texto.lower()
    puntuaciones = {}

    for categoria, terminos in CATEGORIA_MAP.items():
        puntuacion = sum(1 for t in terminos if t in texto_lower)
        if puntuacion > 0:
            puntuaciones[categoria] = puntuacion

    if puntuaciones:
        return max(puntuaciones, key=puntuaciones.get)
    return "otros"


def calcular_relevancia(categoria: str, presupuesto: float) -> float:
    """
    Puntuación precomputada de relevancia según perfil de la organización.
    Combina afinidad de categoría con peso del presupuesto.
    """
    # Categorías de alta prioridad para el perfil de la organización
    pesos_categoria = {
        "tecnología": 8.0,
        "seguridad": 9.0,
        "consultoría": 7.0,
        "formación": 5.0,
        "otros": 2.0,
    }
    peso_base = pesos_categoria.get(categoria, 3.0)

    # Bonus por presupuesto en rango óptimo (50K - 500K EUR)
    if 50_000 <= presupuesto <= 500_000:
        return min(peso_base + 1.5, 10.0)
    elif presupuesto > 500_000:
        return min(peso_base + 0.5, 10.0)

    return peso_base
