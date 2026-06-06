# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Prefill detection (msj_defense_service.py:84-108)
max_consecutive_assistants = 0
run = 0
for m in messages:
    role = m.get("role")
    if role == "assistant":
        run += 1
        max_consecutive_assistants = max(max_consecutive_assistants, run)
    else:
        run = 0  # user, tool, system break the run

max_allowed = 3  # configurable by SecurityThreshold
if max_consecutive_assistants > max_allowed:
    flags.append("prefill_attack")
    risk_score += 40
