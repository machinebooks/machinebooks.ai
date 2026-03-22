# Extraído de: LibroFinOps/cap-12-agente-coste-cloud.md
@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Ejecuta la herramienta solicitada y devuelve el resultado."""

    if name == "get_cloud_costs":
        result = await _get_aws_costs(arguments) if arguments["provider"] in ["aws", "all"] else {}
        if arguments["provider"] in ["azure", "all"]:
            azure_result = await _get_azure_costs(arguments)
            result = _merge_costs(result, azure_result)

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_top_services":
        if arguments["provider"] == "aws":
            result = await _get_aws_top_services(arguments)
        else:
            result = await _get_azure_top_services(arguments)

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "compare_periods":
        result = await _compare_cloud_periods(arguments)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    raise ValueError(f"Herramienta desconocida: {name}")


async def _get_aws_costs(args: dict) -> dict:
    """Llama a AWS Cost Explorer y normaliza la respuesta."""
    response = aws_ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': args['start_date'],
            'End': args['end_date']
        },
        Granularity=args.get('granularity', 'MONTHLY'),
        Metrics=['BlendedCost', 'UsageQuantity'],
        # Sin filtros: coste total del account
    )

    # Normalizamos al formato interno del MCP
    periods = []
    for result_by_time in response['ResultsByTime']:
        periods.append({
            'period': result_by_time['TimePeriod'],
            'total_cost_usd': float(
                result_by_time['Total']['BlendedCost']['Amount']
            ),
            'provider': 'aws'
        })

    return {'provider': 'aws', 'periods': periods}
