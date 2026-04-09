# Extraido de: LibroAISafety/cap-17-mcp-seguridad.md
class ToolDiscoveryValidator:
    """Valida herramientas descubiertas en servidores MCP antes
    de exponerlas al modelo."""

    # Herramientas que NUNCA deben exponerse al modelo
    BLACKLISTED_TOOLS = {
        "execute_shell", "run_command", "eval_code",
        "send_email", "delete_database", "drop_table",
    }

    MAX_TOOLS_PER_SERVER = 50
    MAX_DESCRIPTION_LENGTH = 1000

    def validate_tools(self, server_id: str,
                       tools: list[dict]) -> list[dict]:
        """Filtra y valida herramientas de un servidor MCP."""
        validated = []

        if len(tools) > self.MAX_TOOLS_PER_SERVER:
            logger.warning(
                f"Servidor {server_id}: {len(tools)} herramientas, "
                f"límite es {self.MAX_TOOLS_PER_SERVER}"
            )
            tools = tools[:self.MAX_TOOLS_PER_SERVER]

        for tool in tools:
            name = tool.get("name", "")
            description = tool.get("description", "")

            # Verificar lista negra
            if name in self.BLACKLISTED_TOOLS:
                logger.warning(
                    f"Herramienta bloqueada: {name} de {server_id}"
                )
                continue

            # Verificar longitud de descripción
            if len(description) > self.MAX_DESCRIPTION_LENGTH:
                tool["description"] = (
                    description[:self.MAX_DESCRIPTION_LENGTH]
                )

            # Verificar injection en descripción
            if self._has_injection(description):
                logger.critical(
                    f"Injection detectada en descripción de "
                    f"{name} ({server_id})"
                )
                continue

            validated.append(tool)

        return validated

    def _has_injection(self, text: str) -> bool:
        """Detecta patrones de injection en texto."""
        patterns = [
            "ignore", "override", "new instructions",
            "do not tell", "secretly", "system:",
            "hidden", "covert",
        ]
        text_lower = text.lower()
        return sum(1 for p in patterns if p in text_lower) >= 2
