# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Encolado con prioridad: tarea iniciada por usuario interactivo
analyze_document.apply_async(
    args=[document_id],
    kwargs={"user_id": current_user.id},
    priority=3,  # Alta prioridad: usuario esperando resultado
)

# Encolado con prioridad: tarea programada nocturna
analyze_document.apply_async(
    args=[document_id],
    kwargs={"source": "batch_scheduled"},
    priority=7,  # Prioridad normal: nadie espera en tiempo real
)
