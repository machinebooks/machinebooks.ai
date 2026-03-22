# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/backend/routers/__init__.py
# Registro declarativo de los 35 routers

from importlib import import_module as _imp

modules = [
    # Autenticación
    "auth",                  # /api/auth — login, JWT, sesiones

    # Gaming y CTF
    "gaming",                # /api/gaming — zona de juego, catálogo
    "ctf",                   # /api/ctf — flags, hints, validación
    "challenges",            # /api/challenges — unirse a retos
    "challenge_files",       # /api/challenge-files — ficheros adjuntos
    "scoreboard",            # /api/scoreboard — leaderboards
    "profile",               # /api/profile — stats, skills, badges

    # Escenarios e infraestructura
    "scenario",              # /api/scenario — CRUD escenarios
    "topologies",            # /api/topologies — topologías de red
    "workzones",             # /api/workzones — gestión de workzones
    "catalog",               # /api/catalog — catálogo de templates VM

    # Ataques y simulación
    "attack",                # /api/attack — ejecución de ataques
    "traffic",               # /api/traffic — generación de tráfico
    "ioc",                   # /api/ioc — IOCs y port mirroring

    # Equipos, MITRE y comunidad
    "teams",                 # /api/teams — gestión de equipos
    "mitre_routes",          # /api/mitre — ATT&CK framework
    "community",             # /api/community — foros y contenido compartido

    # Administración (15 routers)
    "admin_dashboard",       # /api/admin/dashboard
    "admin_users",           # /api/admin/users
    "admin_machines",        # /api/admin/machines — Proxmox completo
    "admin_challenges",      # /api/admin/challenges
    "admin_scenarios",       # /api/admin/scenarios
    "admin_workzones",       # /api/admin/workzones
    "admin_attacks",         # /api/admin/attacks
    "admin_playbooks",       # /api/admin/playbooks — Ansible
    "admin_teams",           # /api/admin/teams
    "admin_skills_badges",   # /api/admin/skills-badges
    "admin_database",        # /api/admin/database — SQL console
    "admin_networks",        # /api/admin/networks
    "admin_reports",         # /api/admin/reports
    "admin_audit",           # /api/admin/audit
    "audit_admin",           # /api/audit — auditoría administrativa

    # WebSocket, scripts y 5G
    "ws_deploy",             # /api/ws — despliegues en tiempo real
    "powershell",            # /api/powershell — scripts remotos
    "five_g",                # /api/5g — simulación de redes 5G
]

all_routers = [_imp(f".{m}", package="routers").router for m in modules]
