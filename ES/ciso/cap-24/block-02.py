# Extraído de: LibroCISO/cap-24-calidad-ia.md
class AIMonitoringMetric(Base):
    """Métrica de monitorización con umbrales y tendencia.

    Se calcula periódicamente (tarea Celery) a partir de los
    registros individuales de llm_usage_logs y llm_quality_scores.
    Cada fila es una métrica para un servicio en un período.
    """
    __tablename__ = 'ai_monitoring_metrics'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Qué métrica y para qué servicio
    metric_name = Column(String(100), nullable=False)
    # 'accuracy', 'fairness_dpd', 'drift_psi', 'avg_latency_ms',
    # 'error_rate', 'avg_cost_per_call', 'hallucination_rate',
    # 'groundedness_avg', 'bias_score_avg', 'monthly_cost_usd'
    service_type = Column(String(50), nullable=True)
    # null = métrica global, 'privacy_agent' = métrica del agente

    # Valor calculado
    value = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)

    # Período
    period_type = Column(String(20), nullable=False)  # 'daily', 'weekly'
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Umbrales configurables (se cargan de ai_monitoring_thresholds)
    threshold_warning = Column(Float, nullable=True)
    threshold_alert = Column(Float, nullable=True)
    threshold_critical = Column(Float, nullable=True)

    # Estado actual respecto a umbrales
    status = Column(String(20), nullable=False, default='normal')
    # 'normal', 'warning', 'alert', 'critical'

    # Tendencia respecto al período anterior
    trend = Column(String(20), nullable=True)
    # 'improving', 'stable', 'degrading'
    trend_delta_pct = Column(Float, nullable=True)
    # Variación porcentual: +5.2 = mejoró 5.2%, -3.1 = empeoró 3.1%

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_monitor_metric_period',
              'metric_name', 'service_type', 'period_start'),
    )
