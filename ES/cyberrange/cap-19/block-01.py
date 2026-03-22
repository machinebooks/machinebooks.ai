# Extraído de: LibroCyberrange/cap-19-red-blue-ia.md
# Ejemplo didáctico: patrones/ai_service/blue_team_assistant.py
import anthropic
from datetime import datetime

class BlueTeamAssistant:
    """
    Asistente de IA para el equipo blue team.
    Analiza, correlaciona y recomienda — NUNCA actúa.
    """

    def __init__(self, scenario_id: str, workzone_id: str):
        self.scenario_id = scenario_id
        self.workzone_id = workzone_id
        self.client = anthropic.Anthropic()
        self.alert_history: list[dict] = []
        self.investigation_context: list[dict] = []
        self.tools = self._register_investigation_tools()

    def _register_investigation_tools(self) -> list[dict]:
        """Herramientas de investigación (solo lectura)."""
        return [
            {
                "name": "query_siem",
                "description": (
                    "Ejecuta una consulta contra el SIEM (Wazuh/ELK) "
                    "del escenario. Solo lectura — no modifica alertas."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": [
                                "events_by_ip", "events_by_user",
                                "events_by_process", "events_by_rule",
                                "failed_logins", "lateral_movement_indicators",
                                "privilege_escalation_indicators",
                                "suspicious_network_connections"
                            ]
                        },
                        "filter_value": {"type": "string"},
                        "time_range_minutes": {
                            "type": "integer",
                            "description": "Ventana temporal en minutos"
                        }
                    },
                    "required": ["query_type", "filter_value"]
                }
            },
            {
                "name": "correlate_alerts",
                "description": (
                    "Agrupa alertas relacionadas por indicadores "
                    "compartidos (IP, usuario, hash, timeline)."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "alert_ids": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "correlation_type": {
                            "type": "string",
                            "enum": [
                                "by_source_ip", "by_target_host",
                                "by_user", "by_technique",
                                "temporal_proximity"
                            ]
                        }
                    },
                    "required": ["alert_ids", "correlation_type"]
                }
            },
            {
                "name": "get_asset_context",
                "description": (
                    "Obtiene información de contexto sobre un activo: "
                    "rol, servicios, usuarios, baseline de comportamiento."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "context_type": {
                            "type": "string",
                            "enum": [
                                "asset_info", "normal_baseline",
                                "active_connections", "running_processes",
                                "recent_logins", "installed_services"
                            ]
                        }
                    },
                    "required": ["host", "context_type"]
                }
            },
            {
                "name": "lookup_mitre_technique",
                "description": (
                    "Consulta el framework MITRE ATT&CK para obtener "
                    "detalle de una técnica: descripción, herramientas "
                    "comunes, artefactos forenses, mitigaciones."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "technique_id": {
                            "type": "string",
                            "description": "ID como T1059.001"
                        }
                    },
                    "required": ["technique_id"]
                }
            }
        ]

    async def analyze_alert(self, alert: dict) -> dict:
        """
        Analiza una alerta y genera explicación contextualizada
        con recomendaciones de investigación.
        Usa claude-haiku-4-5 para respuesta rápida.
        """
        self.alert_history.append(alert)

        response = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            system=self._build_blue_system_prompt(),
            messages=[{
                "role": "user",
                "content": f"""Analiza esta alerta del SIEM:

Regla: {alert.get('rule_description', 'N/A')}
Severidad: {alert.get('severity', 'N/A')}
IP origen: {alert.get('source_ip', 'N/A')}
IP destino: {alert.get('dest_ip', 'N/A')}
Usuario: {alert.get('user', 'N/A')}
Proceso: {alert.get('process', 'N/A')}
Timestamp: {alert.get('timestamp', 'N/A')}
Datos raw: {alert.get('raw_data', 'N/A')}

Explica qué significa esta alerta, por qué es relevante,
y qué debería investigar el analista a continuación.
NO ejecutes ninguna acción defensiva — solo recomienda."""
            }]
        )

        return {
            "alert_id": alert.get("id"),
            "analysis": response.content[0].text,
            "model": "claude-haiku-4-5",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def deep_investigation(self, hypothesis: str) -> dict:
        """
        Investigación profunda guiada por una hipótesis del analista.
        Usa claude-sonnet-4-6 con herramientas de investigación.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=self._build_blue_system_prompt(),
            tools=self.tools,
            messages=[{
                "role": "user",
                "content": f"""El analista propone la siguiente hipótesis
de investigación:

"{hypothesis}"

Historial de alertas recientes:
{self._format_recent_alerts(limit=20)}

Investiga esta hipótesis usando las herramientas disponibles.
Consulta el SIEM, correlaciona alertas, enriquece el contexto.

IMPORTANTE:
- Solo investiga. NO tomes acciones defensivas.
- Presenta hallazgos con evidencia concreta (logs, timestamps, IPs).
- Sugiere acciones defensivas que el analista podría ejecutar.
- Indica el nivel de confianza de tus conclusiones (alto/medio/bajo).
- Mapea los hallazgos contra MITRE ATT&CK cuando sea posible."""
            }]
        )

        # Procesar el bucle de tool_use
        investigation = await self._process_investigation(response)
        return investigation

    async def generate_incident_timeline(self) -> dict:
        """
        Genera una línea temporal del incidente basada en todas
        las alertas y la investigación acumulada.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=self._build_blue_system_prompt(),
            tools=self.tools,
            messages=[{
                "role": "user",
                "content": f"""Genera una línea temporal completa
del incidente basándote en:

Alertas registradas: {len(self.alert_history)}
Investigaciones realizadas: {len(self.investigation_context)}

{self._format_all_context()}

Estructura la línea temporal cronológicamente con:
1. Timestamp de cada evento significativo
2. Técnica MITRE ATT&CK correspondiente
3. Hosts y usuarios afectados
4. Evidencia concreta (log entries, IPs, hashes)
5. Confianza en la atribución (alta/media/baja)

Finaliza con un resumen ejecutivo y recomendaciones
de contención que el analista debería considerar."""
            }]
        )

        return {
            "timeline": response.content[0].text,
            "alerts_analyzed": len(self.alert_history),
            "model": "claude-sonnet-4-6",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _build_blue_system_prompt(self) -> str:
        """Prompt del sistema para el asistente blue team."""
        return f"""Eres un analista senior de SOC asistiendo a un equipo
de defensa en un ejercicio de ciberseguridad.

REGLAS INQUEBRANTABLES:
1. NUNCA ejecutes acciones defensivas. Solo analizas y recomiendas.
2. El analista humano toma TODAS las decisiones de contención.
3. Explica las alertas en lenguaje comprensible con contexto técnico.
4. Referencia técnicas MITRE ATT&CK cuando sea relevante.
5. Indica siempre tu nivel de confianza (alto/medio/bajo).
6. Si no estás seguro, di "no tengo suficiente evidencia".

ESCENARIO: {self.scenario_id}
WORKZONE: {self.workzone_id}

Tu objetivo es hacer que el analista humano entienda lo que está
pasando y pueda tomar decisiones informadas de defensa."""

    def _format_recent_alerts(self, limit: int = 10) -> str:
        """Formatea las alertas recientes para incluir en el prompt."""
        recent = self.alert_history[-limit:]
        lines = []
        for alert in recent:
            lines.append(
                f"[{alert.get('timestamp')}] "
                f"Sev:{alert.get('severity')} "
                f"Src:{alert.get('source_ip')} → "
                f"Dst:{alert.get('dest_ip')} "
                f"Rule:{alert.get('rule_description', 'N/A')}"
            )
        return "\n".join(lines)
