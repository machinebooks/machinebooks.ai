# Extraído de: LibroAIGateway/cap-03-pipeline-stages.md
# Firma estándar que comparte TODO stage del pipeline.
# Cada stage recibe el contexto, lo lee y lo escribe, y devuelve.
# Ningún stage llama a otro stage directamente.
async def run(ctx: PipelineContext) -> ResultType:
    ...
