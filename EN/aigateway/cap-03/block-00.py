# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
# Standard signature shared by EVERY stage in the pipeline.
# Each stage receives the context, reads and writes it, and returns.
# No stage calls another stage directly.
async def run(ctx: PipelineContext) -> ResultType:
    ...
