# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/flags/dynamic_flags.py
import hashlib
import secrets
from datetime import datetime
from backend.models import CtfFlag, ChallengeInstance
from backend.database import get_db

class DynamicFlagService:
    """
    Genera flags únicas por participante usando SHA-256 + seed aleatorio.
    Claude define la estructura del reto; este servicio genera el valor
    criptográfico de la flag.
    """

    FLAG_PREFIX = "FLAG"

    def generate_flag(
        self,
        challenge_id: int,
        user_id: int,
        flag_descriptor: str
    ) -> str:
        """
        Genera una flag única para un participante en un reto específico.

        El valor es determinista para la misma combinación de
        (challenge_id, user_id, seed), lo que permite verificación
        sin almacenar la flag en texto claro.

        Args:
            challenge_id: ID del reto
            user_id: ID del participante
            flag_descriptor: Descriptor legible (e.g., "kerberoast_hash")

        Returns:
            String con formato FLAG{hash_hex_12_chars}
        """
        # Seed aleatorio por instancia — almacenado en challenge_instance
        seed = secrets.token_hex(16)

        # Generar hash determinista
        material = f"{challenge_id}:{user_id}:{seed}:{flag_descriptor}"
        flag_hash = hashlib.sha256(material.encode()).hexdigest()[:12]

        flag_value = f"{self.FLAG_PREFIX}{{{flag_hash}}}"

        return flag_value, seed

    def verify_flag(
        self,
        submitted_flag: str,
        challenge_id: int,
        user_id: int,
        seed: str,
        flag_descriptor: str
    ) -> bool:
        """Verifica una flag enviada por un participante."""
        material = f"{challenge_id}:{user_id}:{seed}:{flag_descriptor}"
        expected_hash = hashlib.sha256(material.encode()).hexdigest()[:12]
        expected_flag = f"{self.FLAG_PREFIX}{{{expected_hash}}}"

        # Comparación en tiempo constante para evitar timing attacks
        return secrets.compare_digest(submitted_flag, expected_flag)

    def inject_flags_into_scenario(
        self,
        scenario_data: dict,
        challenge_id: int,
        user_id: int
    ) -> dict:
        """
        Toma un escenario generado por Claude y reemplaza los
        placeholders de flags por valores dinámicos reales.

        Los playbooks de Ansible usan variables {{ flag_N }} que
        este servicio resuelve antes del despliegue.
        """
        flag_values = {}
        seeds = {}

        for flag_def in scenario_data.get("flags", []):
            flag_id = flag_def["id"]
            descriptor = flag_def.get("description", flag_id)

            value, seed = self.generate_flag(
                challenge_id, user_id, descriptor
            )
            flag_values[flag_id] = value
            seeds[flag_id] = seed

        # Inyectar en la configuración de VMs para que los playbooks
        # coloquen las flags en las ubicaciones correctas
        for vm_config in scenario_data.get("vm_configs", []):
            if "custom_config" not in vm_config:
                vm_config["custom_config"] = {}
            vm_config["custom_config"]["flags"] = {
                fid: fval for fid, fval in flag_values.items()
                if any(
                    f["id"] == fid and f.get("location") == vm_config["node_id"]
                    for f in scenario_data.get("flags", [])
                )
            }

        return {
            "scenario_data": scenario_data,
            "flag_values": flag_values,
            "seeds": seeds
        }
