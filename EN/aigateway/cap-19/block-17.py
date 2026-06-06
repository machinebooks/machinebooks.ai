# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Output exfiltration detection (leak_detection_service.py:185-223)
@classmethod
def check_output(cls, response_text: str) -> dict:
    indicators = []
    b64 = _BASE64_BLOCK_RE.search(response_text)  # >=500 chars
    if b64 and _shannon_entropy(b64.group(0)) >= min_entropy:
        indicators.append("large_base64_block")

    if _CREDENTIAL_DUMP_RE.search(response_text):
        indicators.append("credential_dump_pattern")
    if _BULK_EMAIL_RE.search(response_text):
        indicators.append("bulk_email_addresses")
    if _SQL_DUMP_RE.search(response_text):
        indicators.append("sql_dump_fragment")
