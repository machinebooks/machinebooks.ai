# Extraído de: LibroAIGateway/cap-23-compliance-regulatorio.md
# gateway/app/services/compliance_report_service.py:10-23
ENS_MAPPING = [
    {"control": "op.acc.1", "name": "Identificacion",
     "status": "implemented", "feature": "JWT + device fingerprint + MFA"},
    {"control": "mp.info.1", "name": "Datos personales",
     "status": "implemented", "feature": "PII detection + DLP + pseudonymization"},
    {"control": "mp.com.1", "name": "Perimetro seguro",
     "status": "partial", "feature": "Nginx + CORS. Pendiente: WAF"},
    # ... 12 controles en total ...
]
