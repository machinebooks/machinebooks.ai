# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# Manejador global de errores de validación Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Transforma errores de validación en respuestas diagnósticas."""
    logger.error(f"Validation error on {request.method} {request.url}")

    # Intentar capturar el cuerpo para diagnóstico
    try:
        body = await request.body()
        if body:
            logger.error(f"Request body: {body.decode('utf-8')}")
    except Exception:
        logger.error("Could not read request body")

    logger.error(f"Validation errors: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body) if hasattr(exc, 'body') else None
        }
    )
