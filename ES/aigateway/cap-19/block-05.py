# Extraído de: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Enforcement con bypass (jailbreak_detector.py:252-296)
def enforce(text, action_mode="block", threshold=50, bypass=False):
    if action_mode == "off":
        return None

    result = detect(text, threshold=threshold)
    if not result.triggered:
        return result

    if bypass:
        # device_bypass activo: detectamos pero no bloqueamos
        logger.warning("bypass_used severity=%s score=%d", ...)
        return result

    if action_mode == "block":
        raise PolicyBlocked(f"Posible jailbreak: severity={result.severity} ...")
    return result  # log / warn: caller decide
