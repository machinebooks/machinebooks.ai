# Extraído de: LibroTecnico/cap-22-observabilidad.md
class ROITrackerService:
    """Servicio que calcula el ROI de cada tarea completada con IA."""

    def record_task_completion(
        self,
        task_type: str,
        user_id: int,
        ai_duration_seconds: float,
        ai_model: str = None,
        ai_provider: str = None,
        context: dict = None
    ) -> TaskCompletionLog:
        """Registra la compleción de una tarea y calcula el ROI."""

        # Obtiene el baseline configurado para este tipo de tarea
        baseline = HumanBaselineConfig.query.filter_by(
            task_type=task_type,
            is_active=True
        ).first()

        time_saved_minutes = None
        money_saved_eur = None

        if baseline:
            # Tiempo ahorrado = baseline humano - tiempo real con IA
            # Se asume que el usuario aún revisa el resultado (~10% del tiempo base)
            human_review_minutes = baseline.human_baseline_minutes * 0.10
            ai_total_minutes = (ai_duration_seconds / 60) + human_review_minutes

            time_saved_minutes = max(
                0, baseline.human_baseline_minutes - ai_total_minutes
            )
            money_saved_eur = (
                time_saved_minutes / 60
            ) * baseline.human_hourly_cost_eur

        log = TaskCompletionLog(
            user_id=user_id,
            task_type=task_type,
            baseline_id=baseline.id if baseline else None,
            ai_duration_seconds=ai_duration_seconds,
            time_saved_minutes=time_saved_minutes,
            money_saved_eur=money_saved_eur,
            ai_model=ai_model,
            ai_provider=ai_provider,
            context=context,
        )
        db.session.add(log)
        db.session.commit()

        return log

    def get_roi_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "task_type"  # 'task_type' | 'user' | 'model'
    ) -> dict:
        """Agrega el ROI acumulado para el panel Admin."""

        query = db.session.query(
            func.count(TaskCompletionLog.id).label('task_count'),
            func.sum(TaskCompletionLog.time_saved_minutes).label('total_minutes_saved'),
            func.sum(TaskCompletionLog.money_saved_eur).label('total_money_saved')
        ).filter(
            TaskCompletionLog.completed_at.between(start_date, end_date)
        )

        if group_by == "task_type":
            query = query.group_by(TaskCompletionLog.task_type)
        elif group_by == "model":
            query = query.group_by(TaskCompletionLog.ai_provider, TaskCompletionLog.ai_model)

        results = query.all()

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "totals": {
                "tasks_completed": sum(r.task_count for r in results),
                "hours_saved": sum(
                    (r.total_minutes_saved or 0) for r in results
                ) / 60,
                "money_saved_eur": sum(r.total_money_saved or 0 for r in results),
            },
            "breakdown": [
                {
                    "group": getattr(r, group_by, "unknown"),
                    "tasks": r.task_count,
                    "hours_saved": (r.total_minutes_saved or 0) / 60,
                    "money_saved": r.total_money_saved or 0,
                }
                for r in results
            ]
        }
