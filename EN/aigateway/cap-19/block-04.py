# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Multi-turn accumulation boost (jailbreak_detector.py:213-225)
weak_matches = [m for m in matches if 30 <= m.weight < 60]
if len(weak_matches) >= 3:
    score = min(100, int(score * 1.5))
