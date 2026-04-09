# Extracted from: LibroAISafety/ch-17-mcp-security.md
class ToolDiscoveryValidator:
    """Validates tools discovered on MCP servers before
    exposing them to the model."""

    # Tools that should NEVER be exposed to the model
    BLACKLISTED_TOOLS = {
        "execute_shell", "run_command", "eval_code",
        "send_email", "delete_database", "drop_table",
    }

    MAX_TOOLS_PER_SERVER = 50
    MAX_DESCRIPTION_LENGTH = 1000

    def validate_tools(self, server_id: str,
                       tools: list[dict]) -> list[dict]:
        """Filters and validates tools from an MCP server."""
        validated = []

        if len(tools) > self.MAX_TOOLS_PER_SERVER:
            logger.warning(
                f"Server {server_id}: {len(tools)} tools, "
                f"limit is {self.MAX_TOOLS_PER_SERVER}"
            )
            tools = tools[:self.MAX_TOOLS_PER_SERVER]

        for tool in tools:
            name = tool.get("name", "")
            description = tool.get("description", "")

            # Check blacklist
            if name in self.BLACKLISTED_TOOLS:
                logger.warning(
                    f"Tool blocked: {name} from {server_id}"
                )
                continue

            # Check description length
            if len(description) > self.MAX_DESCRIPTION_LENGTH:
                tool["description"] = (
                    description[:self.MAX_DESCRIPTION_LENGTH]
                )

            # Check for injection in description
            if self._has_injection(description):
                logger.critical(
                    f"Injection detected in description of "
                    f"{name} ({server_id})"
                )
                continue

            validated.append(tool)

        return validated

    def _has_injection(self, text: str) -> bool:
        """Detects injection patterns in text."""
        patterns = [
            "ignore", "override", "new instructions",
            "do not tell", "secretly", "system:",
            "hidden", "covert",
        ]
        text_lower = text.lower()
        return sum(1 for p in patterns if p in text_lower) >= 2
