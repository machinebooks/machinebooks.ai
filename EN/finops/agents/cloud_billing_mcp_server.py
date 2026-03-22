# Source: The FinOps Engineer and the Machine -- Chapter 12
# Pattern: MCP server for cloud billing tools

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Executes the requested tool and returns the result."""

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

    raise ValueError(f"Unknown tool: {name}")


async def _get_aws_costs(args: dict) -> dict:
    """Calls AWS Cost Explorer and normalizes the response."""
    response = aws_ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': args['start_date'],
            'End': args['end_date']
        },
        Granularity=args.get('granularity', 'MONTHLY'),
        Metrics=['BlendedCost', 'UsageQuantity'],
        # No filters: total account cost
    )

    # Normalize to MCP internal format
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
