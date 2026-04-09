# Extraido de: LibroAISafety/cap-19-observabilidad.md
# grafana-ai-security-dashboard.json (simplificado a YAML para legibilidad)
# Panel 1: Intentos de injection en el tiempo
- title: "Intentos de Prompt Injection (últimas 24h)"
  type: timeseries
  query: |
    sum(rate(ai_security_injection_attempts_total[5m])) by (severity)
  thresholds:
    - value: 0.1   # >0.1/s = alerta amarilla
      color: yellow
    - value: 1.0   # >1/s = alerta roja
      color: red

# Panel 2: Activaciones de guardrail
- title: "Guardrail Activations (ratio sobre total)"
  type: gauge
  query: |
    sum(rate(ai_security_guardrail_activations_total{action="blocked"}[1h]))
    /
    sum(rate(ai_security_generation_seconds_count[1h]))
  thresholds:
    - value: 0.05  # >5% = amarillo
      color: yellow
    - value: 0.10  # >10% = rojo
      color: red

# Panel 3: PII en respuestas
- title: "PII Detectada en Respuestas"
  type: stat
  query: |
    sum(increase(ai_security_pii_detections_total[24h]))
  thresholds:
    - value: 1     # Cualquier PII = rojo
      color: red

# Panel 4: Anomalías de longitud de respuesta
- title: "Distribución de Longitud de Respuestas"
  type: histogram
  query: |
    histogram_quantile(0.99,
      rate(ai_security_response_length_chars_bucket[1h]))
