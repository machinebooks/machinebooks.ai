# Extraido de: LibroAISafety/cap-17-mcp-seguridad.md
import hashlib
import json
from pathlib import Path

class MCPServerInventory:
    """Inventario y verificación de servidores MCP instalados."""

    def __init__(self, approved_servers_path: str):
        with open(approved_servers_path, encoding="utf-8") as f:
            self._approved = json.load(f)
        # Formato: {"server_name": {"version": "1.2.3",
        #           "hash": "sha256:abc...", "reviewed_date": "..."}}

    def verify_server(self, server_path: Path) -> dict:
        """Verifica un servidor MCP contra el inventario aprobado."""
        # Calcular hash del directorio del servidor
        current_hash = self._hash_directory(server_path)
        server_name = server_path.name

        if server_name not in self._approved:
            return {"status": "UNAPPROVED",
                    "message": f"Servidor '{server_name}' no está "
                               f"en el inventario aprobado"}

        approved = self._approved[server_name]
        if current_hash != approved["hash"]:
            return {"status": "MODIFIED",
                    "message": f"Hash de '{server_name}' no coincide. "
                               f"Esperado: {approved['hash']}, "
                               f"Actual: {current_hash}"}

        return {"status": "VERIFIED",
                "version": approved["version"],
                "reviewed_date": approved["reviewed_date"]}

    def _hash_directory(self, path: Path) -> str:
        """Calcula hash SHA-256 del contenido de un directorio."""
        hasher = hashlib.sha256()
        for file in sorted(path.rglob("*")):
            if file.is_file() and "node_modules" not in str(file):
                hasher.update(file.read_bytes())
        return f"sha256:{hasher.hexdigest()}"
