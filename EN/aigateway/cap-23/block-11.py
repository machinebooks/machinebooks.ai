# Extracted from: LibroAIGateway/cap-23-compliance-regulatory.md
# gateway/app/services/breach_notification_service.py:143-146
safe_title = _html_escape(title or "")
safe_dpo_name = _html_escape(dpo_name or "DPO")
safe_severity = _html_escape(severity or "")
# Details are also escaped individually:
details_html = "".join(
    f"<li>...{_html_escape(str(k))}: {_html_escape(str(v))}...</li>"
    for k, v in details.items()
)
