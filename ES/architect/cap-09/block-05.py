# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: procesamiento de un ítem de feed ATOM
# Patrón: backend/services/opportunities/feed_processor.py

def process_feed_item(item: dict, source_config: dict) -> Optional[Opportunity]:
    """
    Normaliza un ítem de feed ATOM y lo persiste si es nuevo o ha cambiado.
    Retorna la oportunidad procesada o None si es duplicado sin cambios.
    """
    # Calcular hash para detección de cambios
    content_hash = hashlib.sha256(
        f"{item['id']}{item['title']}{item.get('description', '')}".encode()
    ).hexdigest()

    existing = Opportunity.query.filter_by(
        external_id=item["id"],
        source=source_config["name"]
    ).first()

    if existing and existing.content_hash == content_hash:
        return None  # Sin cambios, descartar

    # Mapear campos al modelo interno
    opportunity_data = {
        "external_id":    item["id"],
        "title":          item["title"],
        "description":    item.get("description", ""),
        "estimated_value": parse_budget(item.get("estimated_value")),
        "deadline":       parse_date(item.get("deadline")),
        "entity":         item.get("contracting_entity"),
        "source":         source_config["name"],
        "content_hash":   content_hash,
        "raw_data":       item,  # JSON completo para auditoría
    }

    if existing:
        existing.update(**opportunity_data)
        opportunity = existing
    else:
        opportunity = Opportunity(**opportunity_data)
        db.session.add(opportunity)

    db.session.flush()

    # Lanzar clasificación IA asíncrona
    celery_app.send_task(
        "tasks.ai.classify_opportunity",
        args=[opportunity.id],
        queue="ai"
    )

    return opportunity
