# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
if count < _FAILURE_THRESHOLD:
    return False
# Activate cooldown
until = datetime.utcnow() + timedelta(seconds=_COOLDOWN_DURATION_S)
cooldown = LlmDeploymentCooldown(
    llm_config_id=int(llm_config_id),
    until_ts=until,
    reason=str(reason)[:64],
    failure_count=count,
)
db.add(cooldown)
await db.commit()
