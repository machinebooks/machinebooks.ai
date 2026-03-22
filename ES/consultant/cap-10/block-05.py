# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
proyecto_nuevo = PLANTILLA_ESTIMACION.format(
    tipo_servicio="auditoria",
    sector="financiero",
    complejidad="alta",
    tecnologias="ISO 27001, DORA, SIEM, IAM, cloud híbrido",
    equipo="3",
    descripcion_alcance=(
        "Auditoría combinada ISO 27001 y DORA para entidad financiera. "
        "45 controles de seguridad evaluados, 12 sistemas en alcance, "
        "3 sedes físicas. Incluye revisión de planes de continuidad, "
        "gestión de incidentes y resiliencia operativa digital. "
        "El cliente tiene certificación ISO 27001 vigente y necesita "
        "evaluar el gap para cumplimiento DORA antes de enero 2027."
    ),
    restricciones=(
        "- Cliente con proceso de aprobación de entrevistas lento "
        "(experiencia previa: 2 semanas para agendar).\n"
        "- Un consultor del equipo es junior (primer año).\n"
        "- Documentación del cliente parcialmente en inglés."
    ),
    horas_base="1.200",
    duracion_semanas="8"
)

resultado = ejecutar_estimacion(proyecto_nuevo)
print(resultado["estimacion"])
