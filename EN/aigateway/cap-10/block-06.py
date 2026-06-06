# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/embeddings.py:101-108
adapter = AzureAdapter(
    deployment_name=body.model,
    endpoint=extra.get("endpoint"),
    api_key=extra.get("api_key"),
    api_version=extra.get("api_version"),
)
response = await adapter.embeddings(deployment=body.model, inputs=sanitized_inputs)
