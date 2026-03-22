# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/routers/__init__.py — Registro declarativo de routers
from importlib import import_module as _imp

modules = [
    # "mock_data",    # Datos mock — DESACTIVADO para usar datos reales
    # "debug_auth",   # Debug temporal — ELIMINADO en producción
    "auth",
    "catalog",
    "ws_deploy",
    "scenario",
    "attack",
    "scoreboard",
    "challenges",
    "audit_admin",
    "traffic",
    "topologies",
    "admin_challenge",
    "admin_users",
    "admin_workzones",
    "admin_dashboard",
    "admin_reports",
    "admin_attacks",
    "admin_teams",
    "admin_skills_badges",
    "admin_machines",
    "admin_database",
    "admin_networks",
    "admin_scenarios",
    "workzones",
    "ctf",
    "profile",
    "gaming",
    "teams",
    "challenge_files",
    "admin_playbooks",
    "powershell",
    "mitre_routes",
    "admin_audit",
    "ioc",
    "community",
    "five_g",
]

# Una línea: importa cada módulo y extrae su atributo 'router'
all_routers = [_imp(f".{m}", package="routers").router for m in modules]
