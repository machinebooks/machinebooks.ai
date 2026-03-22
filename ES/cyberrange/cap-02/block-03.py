# Extraído de: LibroCyberrange/cap-02-ciberejercicios.md
# Ejemplo didáctico: mapping de objetivos de ejercicio a MITRE ATT&CK
# Fichero: patrones/mitre/exercise_mitre_mapping.py

from typing import List, Dict, Optional
from pydantic import BaseModel

class MitreMapping(BaseModel):
    """Mapeo de un objetivo de ejercicio a técnicas MITRE ATT&CK."""
    tactic_id: str               # Ej: "TA0006" (Credential Access)
    tactic_name: str             # Ej: "Credential Access"
    technique_id: str            # Ej: "T1558"
    technique_name: str          # Ej: "Steal or Forge Kerberos Tickets"
    subtechnique_id: Optional[str] = None  # Ej: "T1558.003"
    subtechnique_name: Optional[str] = None  # Ej: "Kerberoasting"

    # Indicadores esperados en herramientas de detección
    expected_indicators: List[str] = []
    # Ej: ["Event ID 4769 con cifrado RC4", "Tráfico Kerberos anómalo"]

    # Contramedidas recomendadas
    recommended_mitigations: List[str] = []
    # Ej: ["Usar AES para cuentas de servicio", "Monitorizar TGS requests"]


class ExerciseMitreProfile(BaseModel):
    """Perfil MITRE completo de un ciberejercicio."""
    exercise_id: int
    mappings: List[MitreMapping]

    @property
    def tactics_covered(self) -> List[str]:
        """Tácticas MITRE cubiertas por el ejercicio."""
        return list(set(m.tactic_id for m in self.mappings))

    @property
    def technique_count(self) -> int:
        """Número de técnicas únicas del ejercicio."""
        return len(set(m.technique_id for m in self.mappings))

    def gap_analysis(self, team_detections: List[str]) -> Dict:
        """
        Análisis de gaps: ¿qué técnicas debería haber detectado
        el equipo y no detectó?

        Args:
            team_detections: Lista de technique_ids detectados por el equipo

        Returns:
            Diccionario con técnicas detectadas, no detectadas y porcentaje
        """
        expected = set(m.technique_id for m in self.mappings)
        detected = set(team_detections) & expected
        missed = expected - detected

        return {
            "total_techniques": len(expected),
            "detected": list(detected),
            "detected_count": len(detected),
            "missed": list(missed),
            "missed_count": len(missed),
            "coverage_percent": (len(detected) / len(expected) * 100)
                                if expected else 0,
            # Detalle de técnicas no detectadas con recomendaciones
            "missed_details": [
                {
                    "technique": m.technique_id,
                    "name": m.technique_name,
                    "indicators": m.expected_indicators,
                    "mitigations": m.recommended_mitigations,
                }
                for m in self.mappings
                if m.technique_id in missed
            ],
        }


# Ejemplo: perfil MITRE de un ejercicio de compromiso de AD
AD_COMPROMISE_PROFILE = ExerciseMitreProfile(
    exercise_id=1,
    mappings=[
        MitreMapping(
            tactic_id="TA0006", tactic_name="Credential Access",
            technique_id="T1558", technique_name="Steal or Forge Kerberos Tickets",
            subtechnique_id="T1558.003", subtechnique_name="Kerberoasting",
            expected_indicators=[
                "Event ID 4769 con cifrado RC4 (0x17)",
                "Volumen anómalo de TGS requests desde un único host",
            ],
            recommended_mitigations=[
                "Configurar cuentas de servicio con cifrado AES-256",
                "Monitorizar Event ID 4769 con filtro de cifrado débil",
            ],
        ),
        MitreMapping(
            tactic_id="TA0006", tactic_name="Credential Access",
            technique_id="T1003", technique_name="OS Credential Dumping",
            subtechnique_id="T1003.001", subtechnique_name="LSASS Memory",
            expected_indicators=[
                "Acceso sospechoso a proceso lsass.exe",
                "Herramienta mimikatz o procdump detectada por EDR",
            ],
            recommended_mitigations=[
                "Habilitar Credential Guard en Windows 10/11",
                "Configurar regla SIEM para acceso a LSASS",
            ],
        ),
        MitreMapping(
            tactic_id="TA0008", tactic_name="Lateral Movement",
            technique_id="T1021", technique_name="Remote Services",
            subtechnique_id="T1021.002", subtechnique_name="SMB/Windows Admin Shares",
            expected_indicators=[
                "Conexiones SMB desde hosts no habituales",
                "Uso de PsExec o herramientas similares",
            ],
            recommended_mitigations=[
                "Restringir admin shares con GPO",
                "Segmentar red con reglas de firewall entre segmentos",
            ],
        ),
    ],
)
