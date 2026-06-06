# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Enforcement with bypass (jailbreak_detector.py:252-296)
def enforce(text, action_mode="block", threshold=50, bypass=False):
    if action_mode == "off":
        return None

    result = detect(text, threshold=threshold)
    if not result.triggered:
        return result

    if bypass:
        # device_bypass active: we detect but do not block
        logger.warning("bypass_used severity=%s score=%d", ...)
        return result

    if action_mode == "block":
        raise PolicyBlocked(f"Possible jailbreak: severity={result.severity} ...")
    return result  # log / warn: caller decides
