# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/ia/architecture.py
# Integración de Claude como componente arquitectónico del Cyber Range

import anthropic
from agents import Agent, Runner  # Claude Agent SDK

client = anthropic.Anthropic()

# --- Nivel 1: Generación de escenarios ---
# Claude genera topologías completas, retos y playbooks de Ansible
# a partir de una descripción en lenguaje natural.

scenario_agent = Agent(
    name="scenario_generator",
    model="claude-sonnet-4-6",
    instructions="""Eres un diseñador de ciberejercicios con experiencia
    en entornos militares y corporativos. Genera escenarios que incluyan:
    - Topología de red (VMs, redes, firewalls)
    - Vulnerabilidades a explotar con MITRE ATT&CK T-codes
    - Flags CTF con dificultad progresiva
    - Playbooks de Ansible para despliegue automático""",
    tools=[
        create_vm_template,      # Herramienta: crear template de VM
        define_network,          # Herramienta: definir red
        generate_flag,           # Herramienta: generar flag CTF
        write_playbook,          # Herramienta: generar playbook Ansible
    ]
)

# --- Nivel 2: Coaching adaptativo ---
# Claude analiza las acciones del jugador y ofrece guía sin dar respuestas.
# Usa claude-haiku-4-5 por velocidad: el feedback debe ser inmediato.

coaching_agent = Agent(
    name="adaptive_coach",
    model="claude-haiku-4-5",
    instructions="""Eres un instructor de ciberseguridad. Guía al
    participante hacia la solución sin darla directamente. Analiza
    sus acciones, identifica dónde está atascado y sugiere la
    siguiente dirección de investigación. Nunca reveles flags,
    contraseñas ni exploits directamente.""",
    tools=[
        get_player_actions,      # Herramienta: historial de acciones
        get_challenge_metadata,  # Herramienta: metadatos del reto
        check_progress,          # Herramienta: progreso actual
    ]
)

# --- Nivel 3: Red team automatizado ---
# Agentes con Claude Agent SDK que ejecutan cadenas de ataque
# coherentes basadas en MITRE ATT&CK (capítulo 19).

red_team_agent = Agent(
    name="red_team_operator",
    model="claude-sonnet-4-6",
    instructions="""Eres un operador de red team con experiencia
    en penetration testing. Ejecuta cadenas de ataque coherentes
    siguiendo el framework MITRE ATT&CK. Documenta cada paso
    con T-code, herramienta usada y resultado obtenido.""",
    tools=[
        scan_network,            # Herramienta: reconocimiento
        exploit_vulnerability,   # Herramienta: explotación
        lateral_movement,        # Herramienta: movimiento lateral
        exfiltrate_data,         # Herramienta: exfiltración
        log_mitre_technique,     # Herramienta: registro ATT&CK
    ]
)
