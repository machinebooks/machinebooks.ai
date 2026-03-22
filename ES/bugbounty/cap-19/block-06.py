# Extraído de: LibroBugBounty/cap-19-triage-negociacion.md
import json
from datetime import datetime, timedelta

def check_report_status(reports_file):
    """Verifica estado de reportes y genera alertas."""
    with open(reports_file) as f:
        reports = json.load(f)

    today = datetime.now()
    alerts = []

    for report in reports:
        submitted = datetime.fromisoformat(report["submitted"])
        days = (today - submitted).days
        status = report["status"]

        # Alertas por tiempo sin respuesta
        if status == "submitted" and days > 7:
            alerts.append(f"[!] {report['id']}: {days}d sin triaje")
        if status == "triaged" and days > 30:
            alerts.append(f"[!] {report['id']}: {days}d sin validación")
        if status == "validated" and days > 90:
            alerts.append(f"[!!] {report['id']}: {days}d sin corrección — disclosure eligible")

        # Alertas por bounty pendiente
        if status == "resolved" and not report.get("bounty_paid"):
            alerts.append(f"[$] {report['id']}: resuelto pero sin bounty")

    return alerts
