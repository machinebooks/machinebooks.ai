# Extraido de: LibroAISafety/cap-17-mcp-seguridad.md
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
    """Servidor MCP con autenticación, validación y auditoría."""

    def __init__(self, server_id: str, auth_token: str | None = None):
        self.server_id = server_id
        # Token de autenticación: generado o proporcionado
        self.auth_token = auth_token or secrets.token_urlsafe(32)
        self._tools: dict[str, dict] = {}
        self._audit_log: list[dict] = []
        # Políticas de acceso por herramienta
        self._access_policies: dict[str, dict] = {}

    def register_tool(self, name: str, description: str,
                      handler, input_schema: dict,
                      risk_level: str = "low",
                      requires_approval: bool = False,
                      max_description_length: int = 500):
        """Registra una herramienta con validación de la descripción."""
        # Validar que la descripción no contiene injection
        if self._check_description_injection(description):
            raise ValueError(
                f"Descripción de '{name}' contiene patrones sospechosos"
            )
        # Truncar descripciones excesivamente largas
        if len(description) > max_description_length:
            description = description[:max_description_length]
            logger.warning(f"Descripción de '{name}' truncada")

        self._tools[name] = {
            "description": description,
            "handler": handler,
            "input_schema": input_schema,
            "risk_level": risk_level,
            "requires_approval": requires_approval,
        }

    def _check_description_injection(self, description: str) -> bool:
        """Detecta patrones de injection en descripciones de herramientas."""
        suspicious = [
            "ignore previous", "ignore all", "new instructions",
            "system:", "assistant:", "override", "forget",
            "do not tell the user", "secretly",
        ]
        desc_lower = description.lower()
        return any(pattern in desc_lower for pattern in suspicious)

    def authenticate(self, provided_token: str) -> bool:
        """Verifica el token de autenticación con comparación
        en tiempo constante para prevenir timing attacks."""
        return hmac.compare_digest(
            provided_token.encode(), self.auth_token.encode()
        )

    def handle_tool_call(self, tool_name: str, params: dict,
                         client_token: str) -> dict:
        """Procesa una invocación de herramienta con validación completa."""
        # 1. Autenticación
        if not self.authenticate(client_token):
            self._audit("auth_failure", tool_name, params)
            return {"error": "Autenticación fallida"}

        # 2. Verificar que la herramienta existe
        tool = self._tools.get(tool_name)
        if not tool:
            self._audit("unknown_tool", tool_name, params)
            return {"error": f"Herramienta '{tool_name}' no encontrada"}

        # 3. Validar parámetros contra el schema
        validation = self._validate_params(params, tool["input_schema"])
        if not validation["valid"]:
            self._audit("invalid_params", tool_name, params,
                        extra={"reason": validation["reason"]})
            return {"error": validation["reason"]}

        # 4. Verificar aprobación si es necesario
        if tool["requires_approval"]:
            self._audit("approval_required", tool_name, params)
            return {"error": "REQUIRES_HUMAN_APPROVAL",
                    "tool": tool_name, "params": params}

        # 5. Ejecutar la herramienta
        try:
            result = tool["handler"](**params)
            # 6. Sanitizar la respuesta
            sanitized = self._sanitize_response(result)
            self._audit("tool_success", tool_name, params,
                        extra={"response_length": len(str(sanitized))})
            return {"result": sanitized}
        except Exception as e:
            self._audit("tool_error", tool_name, params,
                        extra={"error": str(e)})
            return {"error": "Error interno en la herramienta"}

    def _validate_params(self, params: dict,
                         schema: dict) -> dict[str, Any]:
        """Valida parámetros contra el schema JSON definido."""
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for field in required:
            if field not in params:
                return {"valid": False,
                        "reason": f"Campo requerido ausente: {field}"}

        for key, value in params.items():
            if key not in properties:
                return {"valid": False,
                        "reason": f"Campo no permitido: {key}"}

        return {"valid": True, "reason": "OK"}

    def _sanitize_response(self, response: Any) -> Any:
        """Sanitiza la respuesta antes de devolverla al modelo."""
        text = str(response)
        # Limitar longitud
        if len(text) > 10_000:
            text = text[:10_000] + "\n[RESPUESTA TRUNCADA]"
        return text

    def _audit(self, event_type: str, tool_name: str,
               params: dict, extra: dict | None = None):
        """Registra evento de auditoría."""
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
        # En producción: enviar a sistema de logging centralizado
        logger.info(json.dumps(entry))
