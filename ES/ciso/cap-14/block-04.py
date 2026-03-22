# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: modelos/ai_monitoring.py
# Métricas de monitorización continua de sistemas de IA

class MetricType(str, Enum):
    ACCURACY = "accuracy"             # Precisión evaluada por supervisores
    FAIRNESS_DPD = "fairness_dpd"     # Demographic Parity Difference
    DRIFT_PSI = "drift_psi"           # Population Stability Index
    LATENCY_P99 = "latency_p99"       # Percentil 99 de latencia (ms)
    ERROR_RATE = "error_rate"         # Tasa de errores
    BIAS_SCORE = "bias_score"         # Evaluación compuesta de sesgo


class AlertLevel(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    ALERT = "alert"
    CRITICAL = "critical"


class MetricTrend(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"


class AIMonitoringMetric(BaseModel):
    """Métrica de monitorización de un sistema de IA.

    Cada registro es un snapshot temporal de una métrica concreta.
    Las series temporales permiten detectar tendencias.
    """
    __tablename__ = "ai_monitoring_metrics"

    ai_record_id = Column(ForeignKey("ai_governance_records.id"), nullable=False)
    metric_type = Column(SQLEnum(MetricType), nullable=False)

    # Valor y umbrales
    value = Column(Float, nullable=False)                  # Valor medido
    threshold_warning = Column(Float)                      # Umbral de warning
    threshold_alert = Column(Float)                        # Umbral de alerta
    threshold_critical = Column(Float)                     # Umbral crítico

    # Estado calculado
    alert_level = Column(SQLEnum(AlertLevel), default=AlertLevel.NORMAL)
    trend = Column(SQLEnum(MetricTrend), default=MetricTrend.STABLE)

    # Contexto
    sample_size = Column(Float)                            # Tamaño de muestra evaluada
    measurement_period = Column(String(50))                # "daily", "weekly", "monthly"
    notes = Column(Text)                                   # Observaciones del evaluador

    # Relación
    ai_record = relationship("AIGovernanceRecord", back_populates="monitoring_metrics")
