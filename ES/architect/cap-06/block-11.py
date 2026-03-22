# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
async def execute(
    self, tool_name: str, arguments: Dict[str, Any],
    security_ctx: SecurityContext = None,
) -> ToolResult:
    """Ejecutar herramienta con validación completa de seguridad.

    Pipeline: verificar existencia → verificar nivel de seguridad
    → sanitizar inputs → aplicar timeout → truncar output → audit log.
    """
    ctx = security_ctx or SecurityContext()

    # 1. Verificar que la herramienta existe en el registro
    tool = self._tools.get(tool_name)
    if not tool:
        return ToolResult(tool_name=tool_name, success=False,
                          error=f"Tool '{tool_name}' no registrada")

    # 2. Verificar nivel de seguridad del usuario
    if tool.security_level == SecurityLevel.ADMIN and not ctx.is_admin:
        logger.warning("tool_access_denied", tool=tool_name,
                       user=ctx.user_id, level="admin")
        return ToolResult(tool_name=tool_name, success=False,
                          error="Acceso denegado: requiere admin")

    # 3. Sanitizar: eliminar parámetros no declarados en el schema
    allowed_keys = set(tool.parameters.get("properties", {}).keys())
    clean_args = {k: v for k, v in arguments.items() if k in allowed_keys}

    # 4. Ejecutar con timeout — el SecurityContext viaja al handler
    result_text = await asyncio.wait_for(
        tool.handler(security_ctx=ctx, **clean_args),
        timeout=tool.timeout_seconds,
    )
    return ToolResult(tool_name=tool_name, success=True, result=result_text)
