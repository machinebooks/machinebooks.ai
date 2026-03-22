# Extraído de: LibroTecnico/cap-22-observabilidad.md
class HumanBaselineConfig(db.Model):
    """Configuración de baseline humano por tipo de tarea.

    Estos valores NO son estimaciones — provienen de mediciones reales
    del proceso manual anterior a la implantación de la Plataforma.
    Se pueden actualizar desde el panel Admin cuando las condiciones cambian.
    """
    __tablename__ = 'human_baseline_configs'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)

    task_type = db.Column(db.String(100), unique=True, nullable=False)
    # 'document_analysis', 'proposal_generation', 'cv_analysis',
    # 'business_intelligence_report', 'opportunity_search'

    # Tiempo baseline en minutos (medido del proceso real anterior)
    human_baseline_minutes = db.Column(db.Float, nullable=False)
    # document_analysis: 480 min (8 horas analista senior)
    # proposal_generation: 2400 min (40 horas, varios perfiles)
    # cv_analysis: 45 min (45 minutos por perfil)

    # Coste por hora del perfil humano que realizaría esta tarea
    human_hourly_cost_eur = db.Column(db.Float, nullable=False)
    # Incluye coste total del empleado: salario + cargas sociales

    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class TaskCompletionLog(db.Model):
    """Registro de tareas completadas con IA con cálculo de ROI.

    Cada vez que un usuario completa una tarea con IA, se registra
    aquí con el cálculo de ahorro. El dashboard Admin agrega estos
    registros para mostrar el ROI acumulado.
    """
    __tablename__ = 'task_completion_logs'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    task_type = db.Column(db.String(100), nullable=False)
    baseline_id = db.Column(
        db.Integer, db.ForeignKey('human_baseline_configs.id'), nullable=True
    )

    # Tiempo real de la tarea con IA
    ai_duration_seconds = db.Column(db.Float, nullable=False)

    # Cálculos derivados (calculados en el momento del registro)
    time_saved_minutes = db.Column(db.Float, nullable=True)
    money_saved_eur = db.Column(db.Float, nullable=True)

    # Modelo IA utilizado (para análisis por proveedor)
    ai_model = db.Column(db.String(100), nullable=True)
    ai_provider = db.Column(db.String(50), nullable=True)

    # Contexto adicional
    context = db.Column(db.JSON, nullable=True)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_task_completion_type_date', 'task_type', 'completed_at'),
        Index('idx_task_completion_user', 'user_id', 'completed_at'),
    )
