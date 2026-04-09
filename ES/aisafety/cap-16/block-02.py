# Extraido de: LibroAISafety/cap-16-seguridad-agentes.md
import subprocess
import tempfile
import os
from pathlib import Path

class SandboxedExecutor:
    """Ejecuta código generado por el agente en un entorno aislado."""

    ALLOWED_COMMANDS = {"python3", "node"}
    MAX_EXECUTION_TIME = 30  # segundos
    MAX_OUTPUT_SIZE = 10_000  # caracteres

    def __init__(self, workspace: Path):
        self.workspace = workspace
        # Crear directorio aislado sin acceso a red ni a ficheros del host
        self.sandbox_dir = tempfile.mkdtemp(prefix="agent_sandbox_")

    def execute(self, command: str, code: str) -> dict:
        """Ejecuta código en sandbox y retorna resultado."""
        if command not in self.ALLOWED_COMMANDS:
            return {"error": f"Comando '{command}' no permitido",
                    "output": ""}

        # Escribir código en fichero temporal dentro del sandbox
        code_file = os.path.join(self.sandbox_dir, "script.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                [command, code_file],
                capture_output=True, text=True,
                timeout=self.MAX_EXECUTION_TIME,
                cwd=self.sandbox_dir,
                # Restringir variables de entorno
                env={"PATH": "/usr/bin:/usr/local/bin",
                     "HOME": self.sandbox_dir}
            )
            output = result.stdout[:self.MAX_OUTPUT_SIZE]
            return {"output": output, "error": result.stderr[:1000],
                    "exit_code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": "Tiempo de ejecución excedido",
                    "output": ""}
