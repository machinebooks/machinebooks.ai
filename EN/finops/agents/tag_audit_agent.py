# Source: The FinOps Engineer and the Machine -- Chapter 5
# Pattern: Claude agent for tag compliance audit

def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Tool dispatcher for the agent."""
    if tool_name == "list_untagged_ec2":
        result = list_untagged_ec2(**tool_input)
        return json.dumps(result)
    elif tool_name == "list_untagged_rds":
        # Analogous implementation for RDS
        return json.dumps([])
    elif tool_name == "propose_tag_correction":
        result = propose_tag_correction(**tool_input)
        return json.dumps(result)
    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def run_tag_audit_agent(region: str = "eu-west-1") -> str:
    """
    Runs the tag audit agent.
    The agent analyzes inventory, infers context, and proposes corrections.
    Returns the final report as text.
    """
    required_tags = ["environment", "team", "service", "cost-center"]

    system_prompt = """You are a FinOps agent specialized in cloud tag auditing.
Your function is:
1. List EC2 and RDS resources without mandatory tags in the indicated region.
2. For each untagged resource, infer probable tag values based on the resource
   name, the VPC it belongs to, existing partial tags, and creation date.
3. Register correction proposals with clear justification and honest confidence level.
4. Generate a summary report with the number of resources audited, proposals generated,
   and estimated impact on spend attribution.

Important:
- Do not execute corrections directly. Only propose.
- If you lack sufficient context to infer a value with medium or high confidence,
  indicate confidence=low and explain what additional information you would need.
- Team values must be one of: backend, frontend, data, platform, security.
- Environment values must be: prod, staging, dev, sandbox."""

    messages = [
        {
            "role": "user",
            "content": (
                f"Audit EC2 and RDS resources in region {region}. "
                f"Mandatory tags: {', '.join(required_tags)}. "
                "Propose corrections for all incorrectly tagged resources."
            ),
        }
    ]

    # Agentic loop: the agent decides when it is done
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=TAG_AUDIT_TOOLS,
            messages=messages,
        )

        # Add agent response to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # The agent has finished. Extract the final text.
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Audit completed without textual report."

        if response.stop_reason == "tool_use":
            # Process requested tools
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})
