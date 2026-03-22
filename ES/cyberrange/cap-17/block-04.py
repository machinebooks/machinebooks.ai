# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/playbook_generator.py
import anthropic
import yaml
import subprocess
import tempfile
from pathlib import Path

class PlaybookGeneratorService:
    """
    Genera playbooks de Ansible para configuración de vulnerabilidades
    que no existen en el catálogo predefinido.

    ADVERTENCIA: Todo playbook generado pasa por validación de sintaxis
    y revisión humana antes de ejecución. Nunca se ejecuta código
    generado por LLM sin supervisión.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()

    async def generate_playbook(
        self,
        vulnerability_description: str,
        target_os: str,
        target_role: str,
        existing_playbooks: list[str]
    ) -> dict:
        """
        Genera un playbook de Ansible para una vulnerabilidad específica.

        Returns:
            dict con el YAML del playbook, resultado de validación
            y advertencias de seguridad.
        """
        # Cargar ejemplos de playbooks existentes como referencia de estilo
        examples = self._load_playbook_examples(target_os)

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system="""Eres un experto en Ansible especializado en configuración
de vulnerabilidades para entornos de entrenamiento en ciberseguridad.

REGLAS:
1. Genera SOLO playbooks de Ansible válidos en formato YAML.
2. Cada tarea debe tener un 'name' descriptivo en español.
3. Usa módulos estándar de Ansible (win_shell, win_regedit, win_service,
   lineinfile, copy, template, etc.). NO uses módulos custom.
4. Incluye comentarios explicando QUÉ vulnerabilidad se introduce y POR QUÉ.
5. NUNCA incluyas tareas destructivas (formatear disco, borrar sistema, etc.).
6. El playbook debe ser IDEMPOTENTE: ejecutarlo dos veces produce el mismo resultado.
7. Incluye un tag 'vulnerability_injection' en todas las tareas.
8. Al final, incluye una tarea de verificación que confirme que la
   vulnerabilidad es explotable.""",
            messages=[{
                "role": "user",
                "content": f"""Genera un playbook de Ansible para la siguiente
vulnerabilidad:

VULNERABILIDAD: {vulnerability_description}
SO OBJETIVO: {target_os}
ROL DE LA MÁQUINA: {target_role}

PLAYBOOKS EXISTENTES EN EL REPOSITORIO (no duplicar):
{chr(10).join(f'- {p}' for p in existing_playbooks)}

EJEMPLOS DE ESTILO (referencia):
{examples}

Genera el playbook completo en formato YAML."""
            }]
        )

        # Extraer YAML del response
        playbook_yaml = self._extract_yaml(response.content[0].text)

        # Validar sintaxis con ansible-lint
        lint_result = await self._validate_with_ansible_lint(playbook_yaml)

        # Validar que no contiene operaciones peligrosas
        safety_check = self._safety_check(playbook_yaml)

        return {
            "playbook_yaml": playbook_yaml,
            "lint_valid": lint_result["valid"],
            "lint_errors": lint_result.get("errors", []),
            "safety_check": safety_check,
            "requires_human_review": True,  # SIEMPRE
            "warning": "Playbook generado por IA — requiere revisión "
                      "humana antes de ejecución en producción"
        }

    async def _validate_with_ansible_lint(self, playbook_yaml: str) -> dict:
        """Valida el playbook con ansible-lint en un directorio temporal."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yml', delete=False
        ) as f:
            f.write(playbook_yaml)
            f.flush()

            try:
                result = subprocess.run(
                    ["ansible-lint", f.name],
                    capture_output=True, text=True, timeout=30
                )
                return {
                    "valid": result.returncode == 0,
                    "errors": result.stdout.splitlines() if result.returncode != 0 else []
                }
            except subprocess.TimeoutExpired:
                return {"valid": False, "errors": ["ansible-lint timeout"]}
            finally:
                Path(f.name).unlink(missing_ok=True)

    def _safety_check(self, playbook_yaml: str) -> dict:
        """
        Verifica que el playbook no contiene operaciones peligrosas
        que podrían afectar al host Proxmox o salir de la workzone.
        """
        dangerous_patterns = [
            "rm -rf /",
            "format c:",
            "dd if=/dev/zero",
            "mkfs",
            "shutdown -h",
            "reboot",
            "iptables -F",  # Podría romper aislamiento de red
        ]

        found_dangerous = []
        yaml_lower = playbook_yaml.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in yaml_lower:
                found_dangerous.append(pattern)

        return {
            "safe": len(found_dangerous) == 0,
            "dangerous_patterns_found": found_dangerous
        }
