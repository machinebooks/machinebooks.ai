# Extraído de: LibroTecnico/cap-11-integracion-llms.md
async with EVALUATION_SEMAPHORE:
    try:
        response = await asyncio.wait_for(
            llm.ainvoke(prompt),
            timeout=120.0
        )
    except asyncio.TimeoutError:
        logger.warning("llm_timeout", service="evaluation")
        raise
