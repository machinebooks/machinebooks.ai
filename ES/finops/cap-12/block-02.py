# Extraído de: LibroFinOps/cap-12-agente-coste-cloud.md
async def _safe_get_aws_costs(args: dict) -> dict:
    """Obtiene costes AWS con gestión de errores que el agente puede interpretar."""
    try:
        return await _get_aws_costs(args)
    except aws_ce_client.exceptions.DataUnavailableException:
        return {
            "error": True,
            "provider": "aws",
            "message": "Datos no disponibles para el periodo solicitado. "
                       "AWS Cost Explorer necesita 24-48h para publicar costes finales.",
            "suggestion": "Prueba con un periodo anterior o usa granularidad MONTHLY."
        }
    except aws_ce_client.exceptions.LimitExceededException:
        return {
            "error": True,
            "provider": "aws",
            "message": "Se ha excedido el límite de solicitudes a AWS Cost Explorer.",
            "suggestion": "Espera unos segundos e intenta con un rango de fechas más amplio."
        }
    except Exception as e:
        return {
            "error": True,
            "provider": "aws",
            "message": f"Error inesperado al consultar AWS: {type(e).__name__}",
            "suggestion": "Verifica que las credenciales AWS estén configuradas."
        }
