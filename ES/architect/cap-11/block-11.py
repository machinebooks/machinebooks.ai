# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/compliance/monitoring_tasks.py
# Estas tareas se ejecutan como Celery Beat tasks

@celery_app.task
def check_pii_in_outputs():
    """
    Escanea outputs de IA de las últimas 6 horas buscando PII.
    Se ejecuta cada 6 horas.
    """
    recent_logs = LLMUsageLog.query.filter(
        LLMUsageLog.timestamp >= datetime.utcnow() - timedelta(hours=6),
        LLMUsageLog.contained_pii == None  # Sin clasificar
    ).all()

    for log in recent_logs:
        pii_detected = pii_detector.scan(log.output_sample)
        log.contained_pii = pii_detected.has_pii
        log.pii_types_detected = pii_detected.types  # DNI, email, IBAN, etc.

        if pii_detected.has_pii and not log.pii_redacted:
            # Alerta inmediata al responsable de privacidad
            compliance_alerter.alert_pii_leak(log)


@celery_app.task
def evaluate_model_bias():
    """
    Evaluación semanal de sesgo por servicio.
    Se ejecuta los lunes a las 06:00.
    """
    for service_type in AI_SERVICE_TYPES:
        recent_scores = LLMQualityScore.query.filter(
            LLMQualityScore.service_type == service_type,
            LLMQualityScore.evaluated_at >= datetime.utcnow() - timedelta(days=7)
        ).all()

        if not recent_scores:
            continue

        avg_bias = sum(s.bias_score for s in recent_scores) / len(recent_scores)

        if avg_bias > BIAS_ALERT_THRESHOLD:  # Default: 0.3
            compliance_alerter.alert_bias_detected(service_type, avg_bias)


@celery_app.task
def verify_config_integrity():
    """
    Verifica que los prompts activos no han sido modificados sin control.
    Se ejecuta cada 12 horas.
    """
    active_prompts = LLMPromptTemplate.query.filter_by(status="active").all()

    for prompt in active_prompts:
        current_hash = hashlib.sha256(prompt.content.encode()).hexdigest()
        if current_hash != prompt.content_hash:
            compliance_alerter.alert_integrity_violation(
                prompt_key=prompt.key,
                stored_hash=prompt.content_hash,
                current_hash=current_hash
            )
