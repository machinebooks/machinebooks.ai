# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
class PowerShellService:
    """Descubre y ejecuta scripts PowerShell en el laboratorio."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.lab_path = self.project_root / "LAB-main"

    async def discover_powershell_scripts(self) -> List[str]:
        """Escanea el directorio LAB-main buscando .ps1, .bat, .cmd"""
        scripts = []
        for path in [self.lab_path] + self.alt_paths:
            if path.exists():
                scripts.extend(self._scan_directory_for_scripts(path))
                break
        return scripts

    async def execute_powershell_script(
        self, script_name: str,
        output_callback: Optional[Callable] = None
    ) -> bool:
        """Ejecuta un script con streaming de output."""
        script_path = await self._find_script_path(script_name)
        if not script_path:
            return False

        if script_path.suffix.lower() == '.ps1':
            cmd = ['powershell.exe', '-ExecutionPolicy', 'Bypass',
                   '-NoProfile', '-File', str(script_path)]
        else:
            cmd = [str(script_path)]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(script_path.parent)
        )

        while True:
            raw = await process.stdout.readline()
            if not raw:
                break
            line = raw.decode(errors="replace")
            if output_callback:
                await output_callback(line.strip())

        await process.wait()
        return process.returncode == 0
