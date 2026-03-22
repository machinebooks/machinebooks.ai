# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/action_tracker.py
import re
from datetime import datetime
from typing import Optional, List
from collections import deque

# Patrones de clasificación de comandos por categoría MITRE
COMMAND_PATTERNS = {
    "recon": [
        r"^nmap\s",          # Escaneo de puertos
        r"^ping\s",          # Descubrimiento de hosts
        r"^whois\s",         # Información de dominio
        r"^dig\s",           # DNS lookup
        r"^host\s",          # Resolución DNS
        r"^traceroute\s",    # Traza de ruta
        r"^masscan\s",       # Escaneo rápido de puertos
    ],
    "enumeration": [
        r"^enum4linux",      # Enumeración SMB/NetBIOS
        r"^smbclient\s",    # Acceso a shares SMB
        r"^rpcclient\s",    # Enumeración RPC
        r"^ldapsearch\s",   # Enumeración LDAP/AD
        r"^gobuster\s",     # Enumeración de directorios web
        r"^dirb\s",         # Fuerza bruta de directorios
        r"^nikto\s",        # Escaneo de vulnerabilidades web
        r"^wpscan\s",       # Escaneo WordPress
        r"^crackmapexec\s", # Enumeración multi-protocolo
        r"^snmpwalk\s",     # Enumeración SNMP
    ],
    "exploitation": [
        r"^msfconsole",      # Metasploit
        r"^searchsploit\s",  # Búsqueda de exploits
        r"^sqlmap\s",        # Inyección SQL automatizada
        r"^hydra\s",         # Fuerza bruta de credenciales
        r"^john\s",          # Cracking de hashes
        r"^hashcat\s",       # Cracking GPU
        r"^python.*exploit", # Scripts de explotación
        r"^curl.*-d\s",     # POST con datos (posible inyección)
    ],
    "post_exploit": [
        r"^sudo\s",          # Intento de escalada
        r"^find.*-perm",     # Búsqueda de SUID/SGID
        r"^cat\s.*/etc/shadow",  # Lectura de hashes
        r"^cat\s.*/etc/passwd",  # Enumeración de usuarios
        r"^getcap\s",        # Capabilities de Linux
        r"^linpeas",         # Enumeración automatizada
        r"^winpeas",         # Enumeración Windows
        r"^whoami",          # Verificación de identidad
        r"^id\b",            # Grupos y permisos
    ],
    "lateral": [
        r"^ssh\s",           # Movimiento vía SSH
        r"^psexec",          # Ejecución remota Windows
        r"^evil-winrm",      # WinRM
        r"^impacket",        # Herramientas Impacket
        r"^xfreerdp",        # RDP
        r"^scp\s",           # Copia remota
        r"^proxychains",     # Pivoting
    ]
}

class ActionTracker:
    """
    Captura y clasifica acciones del jugador en tiempo real.
    Mantiene un buffer circular de las últimas N acciones por sesión.
    """

    def __init__(self, max_actions_per_session: int = 500):
        self._sessions: dict[str, deque] = {}
        self._max = max_actions_per_session

    def track_command(
        self, user_id: int, challenge_id: int, command: str,
        output_summary: Optional[str] = None
    ) -> PlayerAction:
        """
        Registra un comando ejecutado por el jugador.
        Clasifica automáticamente por categoría MITRE.
        """
        session_key = f"{user_id}:{challenge_id}"
        if session_key not in self._sessions:
            self._sessions[session_key] = deque(maxlen=self._max)

        category = self._classify_command(command)

        action = PlayerAction(
            timestamp=datetime.utcnow(),
            command=self._sanitize_command(command),
            category=category,
            output_summary=output_summary
        )

        self._sessions[session_key].append(action)
        return action

    def get_recent_actions(
        self, user_id: int, challenge_id: int, limit: int = 30
    ) -> List[PlayerAction]:
        """Retorna las últimas N acciones significativas."""
        session_key = f"{user_id}:{challenge_id}"
        actions = list(self._sessions.get(session_key, []))
        # Filtrar acciones triviales (cd, ls, clear, pwd)
        significant = [a for a in actions if not self._is_trivial(a.command)]
        return significant[-limit:]

    def get_all_actions(
        self, user_id: int, challenge_id: int
    ) -> List[PlayerAction]:
        """Retorna todas las acciones de la sesión (para evaluación)."""
        session_key = f"{user_id}:{challenge_id}"
        return list(self._sessions.get(session_key, []))

    def _classify_command(self, command: str) -> str:
        """Clasifica un comando por categoría usando patrones regex."""
        cmd_lower = command.strip().lower()
        for category, patterns in COMMAND_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, cmd_lower):
                    return category
        return "other"

    def _sanitize_command(self, command: str) -> str:
        """Elimina información sensible del comando antes de almacenarlo."""
        # Enmascarar posibles contraseñas en parámetros
        sanitized = re.sub(
            r'(-p\s*|--password[= ])\S+',
            r'\1[REDACTED]',
            command
        )
        return sanitized[:500]  # Limitar longitud

    def _is_trivial(self, command: str) -> bool:
        """Determina si un comando es trivial (no aporta contexto)."""
        trivial = {"cd", "ls", "ll", "clear", "pwd", "exit", "history", "cls"}
        base_cmd = command.strip().split()[0].lower() if command.strip() else ""
        return base_cmd in trivial
