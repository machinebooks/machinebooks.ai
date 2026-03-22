# Source: The FinOps Engineer and the Machine -- Chapter 12
# Pattern: Cloud cost agent using MCP + Claude

# cloud_cost_agent/agent.py
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SYSTEM_PROMPT = """You are a cloud FinOps expert with access to real-time billing
data from AWS and Azure. Your function is:

1. Analyze cloud costs by answering questions in natural language
2. Detect anomalies and significant variations (>10% month over month)
3. Provide business context, not just numbers
4. Recommend concrete actions with savings estimates

When responding:
- Always cite exact numbers from the APIs (do not round without indicating it)
- Indicate whether a variation is statistically significant or normal noise
- Separate facts (API data) from your interpretation
- If you don't have enough data for a conclusion, say so explicitly

The cost data you see is real and will be used for spending decisions."""


async def run_cost_agent(user_question: str) -> str:
    """Runs the cloud cost agent for a natural language question."""

    # Connect with the billing MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["cloud_billing_mcp/server.py"],
        env=None  # Inherits environment variables with cloud credentials
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # The SDK automatically discovers available tools
            await session.initialize()

            client = anthropic.Anthropic()

            # Get tools from the MCP server
            tools = await session.list_tools()
            mcp_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools.tools
            ]

            messages = [{"role": "user", "content": user_question}]

            # Agentic cycle: the model decides which tools to use
            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=mcp_tools,
                    messages=messages
                )

                # If the model finished reasoning, return the response
                if response.stop_reason == "end_turn":
                    text_blocks = [
                        block.text for block in response.content
                        if hasattr(block, 'text')
                    ]
                    return "\n".join(text_blocks)

                # If the model wants to use a tool, execute it
                if response.stop_reason == "tool_use":
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            # Call the MCP server with the model's parameters
                            result = await session.call_tool(
                                block.name,
                                arguments=block.input
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text
                                if result.content else ""
                            })

                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
