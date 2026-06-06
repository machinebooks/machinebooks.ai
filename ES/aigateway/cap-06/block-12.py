# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
# Tras cada llamada exitosa o fallida:
await DeploymentRouter.record_latency(redis, deployment_id, latency_ms)
await DeploymentRouter.mark_success(deployment_id, db)
# ó
await DeploymentRouter.mark_failure(deployment_id, db, is_rate_limit=True)
