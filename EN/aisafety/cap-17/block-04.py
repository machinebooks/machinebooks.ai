# Extracted from: LibroAISafety/ch-17-mcp-security.md
import hashlib
import json
import subprocess
from pathlib import Path

class MCPServerInventory:
    """Inventory and verification of installed MCP servers."""

    def __init__(self, approved_servers_path: str):
        with open(approved_servers_path) as f:
            self._approved = json.load(f)
        # Format: {"server_name": {"version": "1.2.3",
        #           "hash": "sha256:abc...", "reviewed_date": "..."}}

    def verify_server(self, server_path: Path) -> dict:
        """Verifies an MCP server against the approved inventory."""
        # Calculate hash of the server directory
        current_hash = self._hash_directory(server_path)
        server_name = server_path.name

        if server_name not in self._approved:
            return {"status": "UNAPPROVED",
                    "message": f"Server '{server_name}' is not "
                               f"in the approved inventory"}

        approved = self._approved[server_name]
        if current_hash != approved["hash"]:
            return {"status": "MODIFIED",
                    "message": f"Hash of '{server_name}' does not match. "
                               f"Expected: {approved['hash']}, "
                               f"Actual: {current_hash}"}

        return {"status": "VERIFIED",
                "version": approved["version"],
                "reviewed_date": approved["reviewed_date"]}

    def _hash_directory(self, path: Path) -> str:
        """Calculates SHA-256 hash of a directory's contents."""
        hasher = hashlib.sha256()
        for file in sorted(path.rglob("*")):
            if file.is_file() and "node_modules" not in str(file):
                hasher.update(file.read_bytes())
        return f"sha256:{hasher.hexdigest()}"
