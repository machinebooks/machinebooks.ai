# Extraído de: LibroCyberrange/cap-19-red-blue-ia.md
# Ejemplo didáctico: patrones/ai_service/red_team_agent.py
import anthropic
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class AttackPhase(str, Enum):
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    EXFILTRATION = "exfiltration"
    COMMAND_AND_CONTROL = "command_and_control"

@dataclass
class CampaignState:
    """Estado completo de la campaña del agente red team."""
    scenario_id: str
    workzone_id: str
    current_phase: AttackPhase = AttackPhase.RECONNAISSANCE
    compromised_hosts: list[str] = field(default_factory=list)
    discovered_hosts: list[str] = field(default_factory=list)
    discovered_services: dict[str, list[dict]] = field(default_factory=dict)
    credentials: list[dict] = field(default_factory=list)
    blocked_techniques: list[str] = field(default_factory=list)
    actions_log: list[dict] = field(default_factory=list)
    mitre_techniques_used: list[str] = field(default_factory=list)
    objectives_completed: list[str] = field(default_factory=list)
    ttl_remaining_seconds: int = 3600

@dataclass
class RedTeamConfig:
    """Configuración del agente red team para un escenario."""
    difficulty: str  # "beginner", "intermediate", "advanced", "expert"
    attack_speed: str  # "slow", "normal", "fast" — cadencia entre pasos
    allowed_techniques: list[str]  # Técnicas MITRE permitidas
    objectives: list[dict]  # Objetivos de la campaña
    stealth_level: str  # "noisy", "moderate", "stealthy" — cuánto ruido genera


class RedTeamAgent:
    """
    Agente red team autónomo que planifica y ejecuta campañas
    de ataque dentro del perímetro de un escenario del Cyber Range.
    """

    def __init__(self, config: RedTeamConfig, state: CampaignState):
        self.config = config
        self.state = state
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-6"  # Escala a opus para APT complejas
        self.tools = self._register_tools()

    def _register_tools(self) -> list[dict]:
        """Registra las herramientas ofensivas disponibles."""
        return [
            {
                "name": "nmap_scan",
                "description": (
                    "Ejecuta un escaneo Nmap contra un host o rango "
                    "dentro de la workzone. Devuelve puertos abiertos, "
                    "servicios y versiones detectadas."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "IP o rango CIDR dentro de la workzone"
                        },
                        "scan_type": {
                            "type": "string",
                            "enum": ["quick", "service_version", "os_detection"],
                            "description": "Tipo de escaneo"
                        }
                    },
                    "required": ["target", "scan_type"]
                }
            },
            {
                "name": "exploit_service",
                "description": (
                    "Intenta explotar un servicio vulnerable en un host. "
                    "Solo funciona si la vulnerabilidad existe en el escenario."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_host": {"type": "string"},
                        "target_port": {"type": "integer"},
                        "technique_id": {
                            "type": "string",
                            "description": "ID de técnica MITRE ATT&CK (ej: T1210)"
                        },
                        "exploit_module": {
                            "type": "string",
                            "description": "Módulo de exploit registrado"
                        }
                    },
                    "required": ["target_host", "target_port", "technique_id"]
                }
            },
            {
                "name": "credential_harvest",
                "description": (
                    "Extrae credenciales de un host comprometido. "
                    "Requiere acceso previo al host."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "method": {
                            "type": "string",
                            "enum": [
                                "lsass_dump", "sam_dump", "kerberoast",
                                "asreproast", "registry_secrets",
                                "file_search", "mimikatz_logonpasswords"
                            ]
                        }
                    },
                    "required": ["host", "method"]
                }
            },
            {
                "name": "lateral_move",
                "description": (
                    "Mueve la sesión a otro host usando credenciales "
                    "obtenidas previamente."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source_host": {"type": "string"},
                        "target_host": {"type": "string"},
                        "method": {
                            "type": "string",
                            "enum": [
                                "psexec", "wmi", "winrm",
                                "pass_the_hash", "ssh_key", "rdp"
                            ]
                        },
                        "credential_id": {"type": "string"}
                    },
                    "required": [
                        "source_host", "target_host",
                        "method", "credential_id"
                    ]
                }
            },
            {
                "name": "exfiltrate_data",
                "description": (
                    "Simula la exfiltración de datos marcados "
                    "como objetivo del escenario."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "data_target": {"type": "string"},
                        "method": {
                            "type": "string",
                            "enum": ["dns_tunnel", "https", "smb_share"]
                        }
                    },
                    "required": ["host", "data_target"]
                }
            },
            {
                "name": "check_defense_status",
                "description": (
                    "Verifica si el equipo azul ha bloqueado un vector "
                    "específico. Devuelve si la ruta sigue viable."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "technique_id": {"type": "string"},
                        "target_host": {"type": "string"}
                    },
                    "required": ["technique_id", "target_host"]
                }
            }
        ]

    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema con el contexto de la campaña."""
        return f"""Eres un operador de red team ejecutando una campaña
de ataque en un ejercicio de entrenamiento de ciberseguridad.

CONTEXTO DEL ESCENARIO:
- Workzone: {self.state.workzone_id}
- Dificultad: {self.config.difficulty}
- Nivel de sigilo: {self.config.stealth_level}
- Fase actual: {self.state.current_phase.value}

HOSTS DESCUBIERTOS: {self.state.discovered_hosts}
SERVICIOS DESCUBIERTOS: {self.state.discovered_services}
HOSTS COMPROMETIDOS: {self.state.compromised_hosts}
CREDENCIALES OBTENIDAS: {len(self.state.credentials)} sets
TÉCNICAS BLOQUEADAS POR EL BLUE TEAM: {self.state.blocked_techniques}

OBJETIVOS DE LA CAMPAÑA:
{self._format_objectives()}

TÉCNICAS MITRE PERMITIDAS: {self.config.allowed_techniques}

REGLAS INQUEBRANTABLES:
1. Solo operas dentro de la workzone asignada.
2. Solo usas las herramientas registradas.
3. Si una técnica está bloqueada, busca alternativas.
4. Adapta tu velocidad al nivel de sigilo configurado.
5. Registra cada acción con su técnica MITRE correspondiente.
6. NO ejecutes acciones destructivas (wipe, format, delete).

Planifica tu siguiente acción basándote en el estado actual
de la campaña y los resultados de acciones previas."""

    def _format_objectives(self) -> str:
        """Formatea los objetivos de la campaña."""
        lines = []
        for obj in self.config.objectives:
            status = "COMPLETADO" if obj["id"] in self.state.objectives_completed else "PENDIENTE"
            lines.append(f"- [{status}] {obj['description']} (target: {obj['target']})")
        return "\n".join(lines)

    async def execute_step(self) -> dict:
        """
        Ejecuta un paso de la campaña.
        Retorna el resultado de la acción para logging.
        """
        # Verificar TTL antes de actuar
        if self.state.ttl_remaining_seconds <= 0:
            return {"status": "campaign_expired", "reason": "TTL agotado"}

        # El agente decide qué hacer basándose en el estado actual
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self._build_system_prompt(),
            tools=self.tools,
            messages=[{
                "role": "user",
                "content": (
                    "Analiza el estado actual de la campaña y ejecuta "
                    "la siguiente acción más efectiva para avanzar hacia "
                    "los objetivos. Explica tu razonamiento antes de actuar."
                )
            }]
        )

        # Procesar tool_use del agente
        result = await self._process_agent_response(response)

        # Actualizar estado de la campaña
        self._update_campaign_state(result)

        # Registrar acción para telemetría (alimenta al blue team)
        self._log_action(result)

        return result

    async def _process_agent_response(self, response) -> dict:
        """Procesa la respuesta del agente, ejecutando herramientas."""
        results = []
        for block in response.content:
            if block.type == "tool_use":
                # Validar que la herramienta está permitida
                if not self._is_tool_allowed(block.name):
                    results.append({
                        "tool": block.name,
                        "status": "blocked",
                        "reason": "Herramienta fuera de perímetro"
                    })
                    continue

                # Ejecutar la herramienta dentro de la workzone
                tool_result = await self._execute_tool(
                    block.name, block.input
                )
                results.append(tool_result)
            elif block.type == "text":
                # El razonamiento del agente se registra para análisis
                results.append({
                    "type": "reasoning",
                    "content": block.text
                })
        return {"actions": results}

    def _is_tool_allowed(self, tool_name: str) -> bool:
        """Verifica que la herramienta está en el inventario autorizado."""
        allowed = {t["name"] for t in self.tools}
        return tool_name in allowed

    async def _execute_tool(self, tool_name: str, params: dict) -> dict:
        """
        Ejecuta una herramienta ofensiva dentro de la workzone.
        La ejecución real ocurre en un contenedor aislado
        con acceso restringido a la VLAN del escenario.
        """
        # Verificar que el target está dentro de la workzone
        if "target" in params or "target_host" in params:
            target = params.get("target") or params.get("target_host")
            if not self._is_within_workzone(target):
                return {
                    "tool": tool_name,
                    "status": "blocked",
                    "reason": f"Target {target} fuera de la workzone"
                }

        # Delegar ejecución al ToolExecutor aislado
        # (implementación en el servicio de backend)
        result = await tool_executor.run(
            tool_name=tool_name,
            params=params,
            workzone_id=self.state.workzone_id,
            timeout=30  # Timeout por herramienta
        )
        return result

    def _update_campaign_state(self, result: dict):
        """Actualiza el estado de la campaña con los resultados."""
        for action in result.get("actions", []):
            if action.get("type") == "reasoning":
                continue

            # Actualizar hosts descubiertos
            if action.get("tool") == "nmap_scan" and action.get("status") == "success":
                for host in action.get("hosts_found", []):
                    if host not in self.state.discovered_hosts:
                        self.state.discovered_hosts.append(host)
                self.state.discovered_services.update(
                    action.get("services", {})
                )

            # Actualizar hosts comprometidos
            if action.get("tool") == "exploit_service" and action.get("status") == "success":
                host = action.get("target_host")
                if host and host not in self.state.compromised_hosts:
                    self.state.compromised_hosts.append(host)

            # Registrar técnica MITRE usada
            technique = action.get("technique_id")
            if technique and technique not in self.state.mitre_techniques_used:
                self.state.mitre_techniques_used.append(technique)

            # Comprobar si una técnica fue bloqueada por el blue team
            if action.get("status") == "blocked_by_defense":
                technique = action.get("technique_id")
                if technique and technique not in self.state.blocked_techniques:
                    self.state.blocked_techniques.append(technique)

    def _is_within_workzone(self, target: str) -> bool:
        """Verifica que un target está dentro del rango de la workzone."""
        from ipaddress import ip_address, ip_network
        workzone_network = self._get_workzone_network()
        try:
            return ip_address(target) in ip_network(workzone_network)
        except ValueError:
            # Si es un CIDR, verificar que es subred de la workzone
            return ip_network(target, strict=False).subnet_of(
                ip_network(workzone_network)
            )
