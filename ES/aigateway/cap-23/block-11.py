# Extraído de: LibroAIGateway/cap-23-compliance-regulatorio.md
# gateway/app/services/breach_notification_service.py:143-146
safe_title = _html_escape(title or "")
safe_dpo_name = _html_escape(dpo_name or "DPO")
safe_severity = _html_escape(severity or "")
# Los detalles también se escapan individualmente:
details_html = "".join(
    f"<li>...{_html_escape(str(k))}: {_html_escape(str(v))}...</li>"
    for k, v in details.items()
)
