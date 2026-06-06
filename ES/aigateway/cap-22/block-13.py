# Extraído de: LibroAIGateway/cap-22-governance-engine.md
@staticmethod
def _matches_tool(rule, tool_name) -> bool:
    if rule.tool_name == "*":
        return True
    if rule.tool_name == tool_name:
        return True
    # Wildcard: "bash*" matches "bash_rm", "bash_grep"
    if rule.tool_name.endswith("*") and tool_name.startswith(rule.tool_name[:-1]):
        return True
    return False
