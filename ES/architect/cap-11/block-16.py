# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Prioridad de documentos para truncamiento selectivo
DOCUMENT_PRIORITY = {
    'requirements': 1,    # Documento principal: nunca truncar
    'specifications': 2,  # Especificaciones técnicas: alta prioridad
    'annexes': 3,         # Anexos: prioridad media
    'templates': 4,       # Plantillas: baja prioridad
}
