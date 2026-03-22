# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
#!/usr/bin/env python3
"""
Servidor MCP para herramientas de seguridad.
Expone funciones del contenedor Docker como tools de Claude Code.
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
import subprocess
import json

server = Server("security-lab")

@server.tool()
async def analyze_pe(path: str) -> str:
    """Analiza un PE/driver con pefile dentro del contenedor Docker."""
    result = subprocess.run(
        ["docker", "exec", "aegis-security-lab",
         "python3", "/lab/scripts/01_pe_analysis.py", path],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout

@server.tool()
async def r2_analyze(path: str, command: str) -> str:
    """Ejecuta un comando de radare2 contra un binario."""
    script = f"""
import r2pipe, json
r2 = r2pipe.open("{path}", flags=["-2"])
r2.cmd("aaa")
result = r2.cmd("{command}")
print(result)
r2.quit()
"""
    result = subprocess.run(
        ["docker", "exec", "aegis-security-lab",
         "python3", "-c", script],
        capture_output=True, text=True, timeout=120
    )
    return result.stdout

@server.tool()
async def compile_poc(source: str, output: str) -> str:
    """Compila un PoC en C para Windows usando mingw."""
    result = subprocess.run(
        ["docker", "exec", "aegis-security-lab",
         "x86_64-w64-mingw32-gcc", "-o", output,
         source, "-lversion"],  # Link con version.dll si necesario
        capture_output=True, text=True, timeout=30
    )
    return result.stdout if result.returncode == 0 else result.stderr
