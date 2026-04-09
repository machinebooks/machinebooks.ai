# Extracted from: LibroAISafety/ch-17-mcp-security.md
import hashlib
import hmac
import json
import logging
import secrets
from datetime import datetime, timezone
from functools import wraps
from typing import Any

logger = logging.getLogger("mcp_security")

class SecureMCPServer:
    """MCP server with authentication, validation, and auditing."""

    def __init__(self, server_id: str, auth_token: str | None = None):
        self.server_id = server_id
        # Authentication token: generated or provided
        self.auth_token = auth_token or secrets.token_urlsafe(32)
        self._tools: dict[str, dict] = {}
        self._audit_log: list[dict] = []
        # Access policies per tool
        self._access_policies: dict[str, dict] = {}

    def register_tool(self, name: str, description: str,
                      handler, input_schema: dict,
                      risk_level: str = "low",
                      requires_approval: bool = False,
                      max_description_length: int = 500):
        """Registers a tool with description validation."""
        # Validate that the description does not contain injection
        if self._check_description_injection(description):
            raise ValueError(
                f"Description of '{name}' contains suspicious patterns"
            )
        # Truncate excessively long descriptions
        if len(description) > max_description_length:
            description = description[:max_description_length]
            logger.warning(f"Description of '{name}' truncated")

        self._tools[name] = {
            "description": description,
            "handler": handler,
            "input_schema": input_schema,
            "risk_level": risk_level,
            "requires_approval": requires_approval,
        }

    def _check_description_injection(self, description: str) -> bool:
        """Detects injection patterns in tool descriptions."""
        suspicious = [
            "ignore previous", "ignore all", "new instructions",
            "system:", "assistant:", "override", "forget",
            "do not tell the user", "secretly",
        ]
        desc_lower = description.lower()
        return any(pattern in desc_lower for pattern in suspicious)

    def authenticate(self, provided_token: str) -> bool:
        """Verifies the authentication token with constant-time
        comparison to prevent timing attacks."""
        return hmac.compare_digest(
            provided_token.encode(), self.auth_token.encode()
        )

    def handle_tool_call(self, tool_name: str, params: dict,
                         client_token: str) -> dict:
        """Processes a tool invocation with full validation."""
        # 1. Authentication
        if not self.authenticate(client_token):
            self._audit("auth_failure", tool_name, params)
            return {"error": "Authentication failed"}

        # 2. Verify the tool exists
        tool = self._tools.get(tool_name)
        if not tool:
            self._audit("unknown_tool", tool_name, params)
            return {"error": f"Tool '{tool_name}' not found"}

        # 3. Validate parameters against the schema
        validation = self._validate_params(params, tool["input_schema"])
        if not validation["valid"]:
            self._audit("invalid_params", tool_name, params,
                        extra={"reason": validation["reason"]})
            return {"error": validation["reason"]}

        # 4. Check approval if required
        if tool["requires_approval"]:
            self._audit("approval_required", tool_name, params)
            return {"error": "REQUIRES_HUMAN_APPROVAL",
                    "tool": tool_name, "params": params}

        # 5. Execute the tool
        try:
            result = tool["handler"](**params)
            # 6. Sanitize the response
            sanitized = self._sanitize_response(result)
            self._audit("tool_success", tool_name, params,
                        extra={"response_length": len(str(sanitized))})
            return {"result": sanitized}
        except Exception as e:
            self._audit("tool_error", tool_name, params,
                        extra={"error": str(e)})
            return {"error": "Internal tool error"}

    def _validate_params(self, params: dict,
                         schema: dict) -> dict[str, Any]:
        """Validates parameters against the defined JSON schema."""
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for field in required:
            if field not in params:
                return {"valid": False,
                        "reason": f"Required field missing: {field}"}

        for key, value in params.items():
            if key not in properties:
                return {"valid": False,
                        "reason": f"Field not allowed: {key}"}

        return {"valid": True, "reason": "OK"}

    def _sanitize_response(self, response: Any) -> Any:
        """Sanitizes the response before returning it to the model."""
        text = str(response)
        # Limit length
        if len(text) > 10_000:
            text = text[:10_000] + "\n[RESPONSE TRUNCATED]"
        return text

    def _audit(self, event_type: str, tool_name: str,
               params: dict, extra: dict | None = None):
        """Logs an audit event."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server_id": self.server_id,
            "event": event_type,
            "tool": tool_name,
            "params_hash": hashlib.sha256(
                json.dumps(params, sort_keys=True).encode()
            ).hexdigest(),
        }
        if extra:
            entry["extra"] = extra
        self._audit_log.append(entry)
        # In production: send to centralized logging system
        logger.info(json.dumps(entry))
