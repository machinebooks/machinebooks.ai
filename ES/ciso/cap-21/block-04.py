# Extraído de: LibroCISO/cap-21-celery-async.md
@shared_task(
    bind=True,
    name="app.tasks.reports.generate_compliance_report",
    queue="reports",
    soft_time_limit=120,
    time_limit=150,
)
def generate_compliance_report(self, report_id: int, tenant_id: int,
                                framework_ids: list[int],
                                format: str = "pdf",
                                include_ai_summary: bool = False):
    """
    Genera un informe de cumplimiento para uno o varios marcos.
    Actualiza progreso para feedback visual al usuario.
    """
    from app.models import Report, ReportStatus
    from app.services.report_builder import ComplianceReportBuilder
    from app.database import get_session

    session = get_session()
    report = session.get(Report, report_id)
    report.status = ReportStatus.GENERATING
    session.commit()

    try:
        builder = ComplianceReportBuilder(tenant_id=tenant_id)
        total_steps = len(framework_ids) * 3  # datos + render + merge por marco

        for i, fw_id in enumerate(framework_ids):
            # Paso 1: Recopilar datos del marco
            step = i * 3 + 1
            self.update_state(state="PROGRESS", meta={
                "progress": int(step / total_steps * 90),
                "phase": f"Recopilando datos del marco {i+1}/{len(framework_ids)}",
            })
            data = builder.collect_framework_data(fw_id)

            # Paso 2: Renderizar sección
            step = i * 3 + 2
            self.update_state(state="PROGRESS", meta={
                "progress": int(step / total_steps * 90),
                "phase": f"Renderizando sección {i+1}/{len(framework_ids)}",
            })
            builder.render_section(fw_id, data)

            # Paso 3: Si se solicita, generar resumen con IA
            if include_ai_summary:
                step = i * 3 + 3
                self.update_state(state="PROGRESS", meta={
                    "progress": int(step / total_steps * 90),
                    "phase": f"Generando resumen IA para marco {i+1}",
                })
                builder.generate_ai_summary(fw_id, data)

        # Paso final: compilar documento
        self.update_state(state="PROGRESS", meta={
            "progress": 95,
            "phase": f"Compilando documento {format.upper()}",
        })
        file_path = builder.compile(format=format)

        report.status = ReportStatus.COMPLETED
        report.file_path = file_path
        report.file_size_bytes = file_path.stat().st_size
        report.completed_at = datetime.utcnow()
        session.commit()

        return {"report_id": report_id, "file_path": str(file_path)}

    except Exception as exc:
        report.status = ReportStatus.FAILED
        report.error_message = str(exc)[:500]
        session.commit()
        raise
