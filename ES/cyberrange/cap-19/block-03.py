# Extraído de: LibroCyberrange/cap-19-red-blue-ia.md
# Ejemplo didáctico: patrones/ai_service/rl_defense_trainer.py
from dataclasses import dataclass
import numpy as np

@dataclass
class DefenseState:
    """Estado observable para el agente RL defensivo."""
    active_alerts: list[dict]        # Alertas SIEM activas
    network_flows: list[dict]        # Flujos de red recientes
    compromised_indicators: list[str] # IoCs detectados
    available_actions: list[str]      # Acciones defensivas posibles
    time_since_last_alert: float     # Segundos desde última alerta

@dataclass
class DefenseAction:
    """Acción que el agente RL puede tomar."""
    action_type: str  # "block_ip", "isolate_host", "create_rule", "escalate", "ignore"
    target: str       # IP, host o regla afectada
    confidence: float # Confianza del agente en la acción

class CyberDefenseEnvironment:
    """
    Entorno de entrenamiento RL para defensa cibernética.
    Usa el Cyber Range como simulador: el red team agent genera
    ataques, el entorno observa la telemetría, y el agente RL
    aprende a defender.
    """

    def __init__(self, scenario_id: str, red_agent: RedTeamAgent):
        self.scenario_id = scenario_id
        self.red_agent = red_agent
        self.current_state = DefenseState(
            active_alerts=[],
            network_flows=[],
            compromised_indicators=[],
            available_actions=[
                "block_ip", "isolate_host",
                "create_detection_rule", "escalate_to_human",
                "monitor_and_wait"
            ],
            time_since_last_alert=0.0
        )

    def step(self, action: DefenseAction) -> tuple:
        """
        Ejecuta un paso del entorno:
        1. El agente RL toma una acción defensiva
        2. El red team agent ejecuta su siguiente paso
        3. El entorno calcula la recompensa

        Returns: (next_state, reward, done, info)
        """
        # Aplicar acción defensiva
        defense_result = self._apply_defense(action)

        # El red team reacciona
        red_result = self.red_agent.execute_step_sync()

        # Calcular recompensa
        reward = self._calculate_reward(
            defense_result=defense_result,
            red_result=red_result,
            action=action
        )

        # Actualizar estado
        self.current_state = self._observe_state()

        # Verificar si el episodio terminó
        done = self._is_episode_done()

        return self.current_state, reward, done, {
            "defense": defense_result,
            "red_team": red_result
        }

    def _calculate_reward(
        self,
        defense_result: dict,
        red_result: dict,
        action: DefenseAction
    ) -> float:
        """
        Función de recompensa que equilibra detección vs. falsos positivos.

        Recompensas positivas:
        - Bloquear un ataque real: +10
        - Detectar un ataque sin bloquear (alertar): +5
        - Escalar correctamente un incidente complejo: +8

        Penalizaciones:
        - Falso positivo (bloquear tráfico legítimo): -8
        - No detectar un ataque real: -15
        - Acción tardía (ataque progresó antes de la respuesta): -3
        """
        reward = 0.0

        # ¿La acción bloqueó un ataque real?
        if defense_result.get("blocked_real_attack"):
            reward += 10.0

        # ¿La acción causó un falso positivo?
        if defense_result.get("false_positive"):
            reward -= 8.0

        # ¿El red team avanzó sin ser detectado?
        if red_result.get("status") == "success":
            if not defense_result.get("detected"):
                reward -= 15.0
            else:
                reward -= 3.0  # Detectó pero no a tiempo

        # Penalizar inacción excesiva
        if action.action_type == "monitor_and_wait":
            if len(self.current_state.active_alerts) > 5:
                reward -= 2.0  # Acumulación peligrosa de alertas

        return reward

    def _observe_state(self) -> DefenseState:
        """Construye el estado observable desde la telemetría."""
        # Consultar SIEM por alertas activas
        alerts = self._query_siem_alerts()
        # Consultar flujos de red recientes
        flows = self._query_network_flows()
        # Consultar IoCs detectados
        iocs = self._query_detected_iocs()

        return DefenseState(
            active_alerts=alerts,
            network_flows=flows,
            compromised_indicators=iocs,
            available_actions=self.current_state.available_actions,
            time_since_last_alert=self._time_since_last_alert()
        )
