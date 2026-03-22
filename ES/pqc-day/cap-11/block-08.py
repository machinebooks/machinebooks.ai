# Extraído de: LibroPQC/cap-11-analisis-semantico.md
# Score PQC basado en hallazgos por severidad
pqc_risk_score = (
    severity_counts['critical'] * 25 +
    severity_counts['high'] * 15 +
    severity_counts['medium'] * 5 +
    severity_counts['low'] * 1
)
pqc_risk_score = min(100, pqc_risk_score)  # Tope en 100

# Score OWASP (separado)
owasp_risk_score = (
    owasp_severity_counts['critical'] * 25 + ...
)

# Score combinado: PQC pesa más (60/40)
combined_risk_score = int(
    (pqc_risk_score * 0.6) + (owasp_risk_score * 0.4)
)
