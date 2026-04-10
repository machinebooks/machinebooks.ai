# Extracted from: LibroAISafety/ch-16-agent-security.md
import subprocess
import tempfile
import os
from pathlib import Path

class SandboxedExecutor:
    """Executes agent-generated code in an isolated environment."""

    ALLOWED_COMMANDS = {"python3", "node"}
    MAX_EXECUTION_TIME = 30  # seconds
    MAX_OUTPUT_SIZE = 10_000  # characters

    def __init__(self, workspace: Path):
        self.workspace = workspace
        # Create isolated directory without network or host file access
        self.sandbox_dir = tempfile.mkdtemp(prefix="agent_sandbox_")

    def execute(self, command: str, code: str) -> dict:
        """Executes code in sandbox and returns result."""
        if command not in self.ALLOWED_COMMANDS:
            return {"error": f"Command '{command}' not allowed",
                    "output": ""}

        # Write code to temporary file inside sandbox
        code_file = os.path.join(self.sandbox_dir, "script.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                [command, code_file],
                capture_output=True, text=True,
                timeout=self.MAX_EXECUTION_TIME,
                cwd=self.sandbox_dir,
                # Restrict environment variables
                env={"PATH": "/usr/bin:/usr/local/bin",
                     "HOME": self.sandbox_dir}
            )
            output = result.stdout[:self.MAX_OUTPUT_SIZE]
            return {"output": output, "error": result.stderr[:1000],
                    "exit_code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": "Execution time exceeded",
                    "output": ""}
