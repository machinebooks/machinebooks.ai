# Extracted from: LibroAIGateway/cap-23-compliance-regulatory.md
# gateway/app/services/compliance_report_service.py:10-23
ENS_MAPPING = [
    {"control": "op.acc.1", "name": "Identification",
     "status": "implemented", "feature": "JWT + device fingerprint + MFA"},
    {"control": "mp.info.1", "name": "Personal data",
     "status": "implemented", "feature": "PII detection + DLP + pseudonymization"},
    {"control": "mp.com.1", "name": "Secure perimeter",
     "status": "partial", "feature": "Nginx + CORS. Pending: WAF"},
    # ... 12 controls in total ...
]
