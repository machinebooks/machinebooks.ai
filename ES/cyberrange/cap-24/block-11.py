# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Exportación de logs de auditoría
# Fichero: cyber-range-builder/backend/routers/admin_audit.py

@router.post("/export")
def export_audit_data(
    export_request: AuditExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exportar datos de auditoría con filtros y límite de seguridad.
    Formatos: CSV, JSON. Máximo 50.000 registros por exportación."""
    filters = export_request.filters or AuditLogFilter()
    logs, total = AuditService.get_logs(
        db, filters, skip=0,
        limit=min(export_request.max_records, 50000)  # Límite de seguridad
    )

    # La propia exportación se registra en auditoría
    AuditService.log_event(
        db=db,
        event_type='admin_action',
        category='data_access',
        action='export_audit_data',
        description=f"Usuario {current_user.email} exportó "
                    f"{len(logs)} registros en formato "
                    f"{export_request.format}",
        user_id=current_user.id,
        username=current_user.email,
        module='audit',
        function='export_audit_data',
        details={
            'format': export_request.format,
            'record_count': len(logs),
            'include_details': export_request.include_details
        }
    )

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    if export_request.format == 'csv':
        return _generate_csv_export(logs, export_request.include_details, timestamp)
    elif export_request.format == 'json':
        return _generate_json_export(logs, export_request.include_details, timestamp)
