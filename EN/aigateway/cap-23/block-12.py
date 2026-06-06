# Extracted from: LibroAIGateway/cap-23-compliance-regulatory.md
# gateway/app/services/compliance_report_service.py:266-303
return {
    "report_date": datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z"),
    "summary": {
        "total_requests": total_requests,
        "compliance_score": round(score, 1),  # 0-100
        # ... security and data metrics ...
    },
    "security_events": { "total": ..., "by_type": [...], "critical": [...] },
    "audit_integrity": { "sealed_logs": ..., "unsealed_logs": ... },
    "data_protection": { "pii_detections": ..., "dsar_requests": ... },
    "recommendations": [
        "compliance.recommend.activate_mfa",
        "compliance.recommend.configure_siem",
        # ...
    ],
}
