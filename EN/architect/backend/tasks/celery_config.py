"""
Chapter 8: Celery configuration — 4 workers, 7 queues, 14 Beat tasks.

Worker topology:
  - celery_default:    -Q default,sync,crm,priority  -c 4
  - celery_ai:         -Q ai,documents               -c 2
  - celery_automation: -Q automation                  -c 1
  - celery_beat:       scheduler only (no workers)

Queue design rationale:
  - Separate AI tasks from business tasks (different resource profiles)
  - Automation queue isolated (Selenium sessions are long-lived)
  - Priority queue for critical alerts
  - Beat tasks scheduled in off-peak hours (01:00-05:00 UTC)

Rate limiting by task type:
  - AI tasks: 30/min (token cost control)
  - Automation: 5/min (Selenium sessions are expensive)
  - Documents: 10/min (I/O bound)
"""

from celery import Celery
from celery.schedules import crontab


# =============================================================================
# Celery app (Chapter 8)
# =============================================================================

app = Celery("plataforma")

app.conf.update(
    broker_url="redis://redis:6379/1",
    result_backend="redis://redis:6379/2",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # Re-queue if worker crashes mid-task
    worker_prefetch_multiplier=1,  # Fair distribution across workers
)


# =============================================================================
# Task routing (Chapter 8)
# =============================================================================

app.conf.task_routes = {
    # AI tasks -> ai queue (celery_ai worker)
    "tasks.ai.analyze_document":    {"queue": "ai"},
    "tasks.ai.generate_proposal":   {"queue": "ai"},
    "tasks.ai.analyze_cv":          {"queue": "ai"},
    "tasks.ai.score_opportunity":   {"queue": "ai"},
    "tasks.ai.compliance_check":    {"queue": "ai"},

    # Document processing -> documents queue (celery_ai worker)
    "tasks.documents.process_upload": {"queue": "documents"},
    "tasks.documents.index_vectors":  {"queue": "documents"},
    "tasks.documents.reindex_rag":    {"queue": "documents"},

    # RPA automation -> automation queue (celery_automation worker)
    "tasks.automation.crm_bot":       {"queue": "automation"},
    "tasks.automation.portal_bot":    {"queue": "automation"},
    "tasks.automation.pricing_bot":   {"queue": "automation"},
    "tasks.automation.reporting_bot": {"queue": "automation"},

    # CRM sync -> crm queue (celery_default worker)
    "tasks.sync.crm_opportunities":   {"queue": "crm"},
    "tasks.sync.crm_accounts":        {"queue": "crm"},

    # General sync -> sync queue (celery_default worker)
    "tasks.sync.meilisearch_reindex": {"queue": "sync"},
    "tasks.sync.gdpr_cleanup":        {"queue": "sync"},

    # Critical alerts -> priority queue (celery_default worker)
    "tasks.alerts.proactive_scan":    {"queue": "priority"},
    "tasks.alerts.compliance_alert":  {"queue": "priority"},
}


# =============================================================================
# Beat schedule — 14 scheduled tasks (Chapter 8)
# =============================================================================

app.conf.beat_schedule = {

    # --- CRM Sync ------------------------------------------------------------
    "sync-crm-opportunities": {
        "task": "tasks.sync.crm_opportunities",
        "schedule": 300,                          # Every 5 minutes
        "options": {"queue": "crm"},
    },
    "sync-crm-accounts": {
        "task": "tasks.sync.crm_accounts",
        "schedule": 600,                          # Every 10 minutes
        "options": {"queue": "crm"},
    },

    # --- AI Compliance & Governance ------------------------------------------
    "check-ai-compliance": {
        "task": "tasks.ai.compliance_check",
        "schedule": crontab(minute=0, hour="*/6"),   # Every 6 hours
        "options": {"queue": "ai"},
    },
    "detect-pii-in-outputs": {
        "task": "tasks.ai.pii_detection",
        "schedule": crontab(minute=0, hour="*/6"),
        "options": {"queue": "ai"},
    },
    "evaluate-ai-bias": {
        "task": "tasks.ai.bias_evaluation",
        "schedule": crontab(minute=0, hour=6, day_of_week=1),  # Monday 06:00
        "options": {"queue": "ai"},
    },
    "verify-config-integrity": {
        "task": "tasks.ai.config_integrity_check",
        "schedule": crontab(minute=0, hour="*/12"),  # Every 12 hours
        "options": {"queue": "ai"},
    },

    # --- GDPR & Data Cleanup ------------------------------------------------
    "gdpr-daily-cleanup": {
        "task": "tasks.sync.gdpr_cleanup",
        "schedule": crontab(minute=0, hour=2),       # Daily 02:00
        "options": {"queue": "sync"},
    },
    "gdpr-anonymize-old-logs": {
        "task": "tasks.sync.anonymize_audit_logs",
        "schedule": crontab(minute=0, hour=3),       # Daily 03:00
        "options": {"queue": "sync"},
    },

    # --- Indexing & Search ---------------------------------------------------
    "reindex-meilisearch": {
        "task": "tasks.sync.meilisearch_reindex",
        "schedule": crontab(minute=0, hour=1),       # Daily 01:00
        "options": {"queue": "sync"},
    },
    "reindex-rag-vectors": {
        "task": "tasks.documents.reindex_rag",
        "schedule": crontab(minute=0, hour=4),       # Daily 04:00
        "options": {"queue": "documents"},
    },

    # --- Opportunity Engine --------------------------------------------------
    "scan-new-opportunities": {
        "task": "tasks.sync.scan_opportunities",
        "schedule": crontab(minute=0, hour="*/12"),  # Every 12 hours
        "options": {"queue": "sync"},
    },

    # --- Proactive Alerts (Chapter 8 + Chapter 9) ---------------------------
    "proactive-opportunity-alerts": {
        "task": "tasks.alerts.proactive_scan",
        "schedule": crontab(minute=0),               # Every hour
        "options": {"queue": "priority"},
    },

    # --- System Maintenance --------------------------------------------------
    "cleanup-expired-tasks": {
        "task": "tasks.sync.cleanup_task_results",
        "schedule": crontab(minute=30, hour=0),      # Daily 00:30
        "options": {"queue": "sync"},
    },
    "health-check-services": {
        "task": "tasks.sync.platform_health_check",
        "schedule": 300,                             # Every 5 minutes
        "options": {"queue": "default"},
    },
}
