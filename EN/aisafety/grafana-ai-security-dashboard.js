# Extracted from: LibroAISafety/ch-19-observability.md
# grafana-ai-security-dashboard.json (simplified to YAML for readability)
# Panel 1: Injection attempts over time
- title: "Prompt Injection Attempts (last 24h)"
  type: timeseries
  query: |
    sum(rate(ai_security_injection_attempts_total[5m])) by (severity)
  thresholds:
    - value: 0.1   # >0.1/s = yellow alert
      color: yellow
    - value: 1.0   # >1/s = red alert
      color: red

# Panel 2: Guardrail activations
- title: "Guardrail Activations (ratio over total)"
  type: gauge
  query: |
    sum(rate(ai_security_guardrail_activations_total{action="blocked"}[1h]))
    /
    sum(rate(ai_security_generation_seconds_count[1h]))
  thresholds:
    - value: 0.05  # >5% = yellow
      color: yellow
    - value: 0.10  # >10% = red
      color: red

# Panel 3: PII in responses
- title: "PII Detected in Responses"
  type: stat
  query: |
    sum(increase(ai_security_pii_detections_total[24h]))
  thresholds:
    - value: 1     # Any PII = red
      color: red

# Panel 4: Response length anomalies
- title: "Response Length Distribution"
  type: histogram
  query: |
    histogram_quantile(0.99,
      rate(ai_security_response_length_chars_bucket[1h]))
