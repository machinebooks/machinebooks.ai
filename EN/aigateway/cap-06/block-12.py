# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
# After each successful or failed call:
await DeploymentRouter.record_latency(redis, deployment_id, latency_ms)
await DeploymentRouter.mark_success(deployment_id, db)
# or
await DeploymentRouter.mark_failure(deployment_id, db, is_rate_limit=True)
