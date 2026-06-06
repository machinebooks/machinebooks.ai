# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
@classmethod
def build_adapter(cls, config: LLMConfig, deployment: LLMModelDeployment | None = None):
    if deployment is None:
        return get_adapter(config.provider, config.extra_params)
    extras = dict(config.extra_params or {})
    if deployment.endpoint:
        extras["endpoint"] = deployment.endpoint
    if deployment.api_key:
        extras["api_key"] = deployment.api_key
    if deployment.region:
        extras["region"] = deployment.region
    extras["_n7x_deployment_id"] = deployment.id
    provider = (deployment.provider_type or config.provider or "").strip()
    return get_adapter(provider, extras)
