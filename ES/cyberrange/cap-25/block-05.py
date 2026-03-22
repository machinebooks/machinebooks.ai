# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/backend/execution_streaming.py
import asyncio, os, uuid, tempfile, json
from datetime import datetime

class ExecutionService:
    """Ejecución de playbooks Ansible con streaming vía WebSocket."""

    @staticmethod
    async def _run_ansible_streaming(
        execution_id: int,
        session_id: str,
        playbook_id: int
    ):
        db = SessionLocal()
        pb_file = inv_file = vars_file = None

        try:
            playbook = db.query(Playbook).filter_by(id=playbook_id).first()
            execution = db.query(PlaybookExecution).filter_by(id=execution_id).first()

            execution.status = 'running'
            db.commit()

            # 1. Escribir playbook a fichero temporal
            tmp_dir = tempfile.gettempdir()
            pb_file = os.path.join(tmp_dir, f"playbook_{uuid.uuid4().hex[:12]}.yml")
            with open(pb_file, 'w') as f:
                f.write(playbook.playbook_content)

            # 2. Escribir inventario si existe
            if playbook.inventory_content:
                inv_file = os.path.join(tmp_dir, f"inventory_{uuid.uuid4().hex[:12]}.ini")
                with open(inv_file, 'w') as f:
                    f.write(playbook.inventory_content)

            # 3. Merge de variables (playbook + ejecución específica)
            merged_vars = {
                **(playbook.variables_extra or {}),
                **(execution.variables_used or {})
            }
            if merged_vars:
                vars_file = os.path.join(tmp_dir, f"vars_{uuid.uuid4().hex[:12]}.json")
                with open(vars_file, 'w') as f:
                    json.dump(merged_vars, f)

            # 4. Construir comando ansible-playbook
            cmd = ['ansible-playbook', pb_file]
            if inv_file:
                cmd.extend(['-i', inv_file])
            if vars_file:
                cmd.extend(['--extra-vars', f'@{vars_file}'])

            # 5. Ejecutar con subprocess asíncrono y captura línea a línea
            env = os.environ.copy()
            env['ANSIBLE_FORCE_COLOR'] = 'false'
            # HOST_KEY_CHECKING desactivado: las VMs de escenario son
            # efímeras y sus host keys cambian en cada despliegue.
            # No aplicable a sistemas de producción persistentes.
            env['ANSIBLE_HOST_KEY_CHECKING'] = 'false'

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env
            )

            output_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode('utf-8', errors='replace').rstrip()
                output_lines.append(line_str)
                # Enviar cada línea al frontend vía WebSocket
                await stream_to_websocket(session_id, line_str, "ansible")

            return_code = await process.wait()
            execution.output_log = '\n'.join(output_lines)
            execution.status = 'completed' if return_code == 0 else 'failed'
            execution.completed_at = datetime.utcnow()
            db.commit()

        finally:
            # Limpieza segura de ficheros temporales
            safe_tmp = os.path.realpath(tempfile.gettempdir())
            for f in [pb_file, inv_file, vars_file]:
                if f and os.path.exists(f):
                    if os.path.realpath(f).startswith(safe_tmp):
                        os.unlink(f)
            db.close()
