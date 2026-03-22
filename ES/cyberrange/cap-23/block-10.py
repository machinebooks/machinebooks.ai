# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: services/execution_service.py
class ExecutionService:
    """Servicio de ejecución con streaming WebSocket integrado"""

    @staticmethod
    def start_execution(db: Session, execution_data, background_tasks,
                        session_id: str = None) -> tuple:
        """Iniciar ejecución de playbook con sesión WebSocket"""
        if not session_id:
            session_id = str(uuid.uuid4())

        playbook = db.query(Playbook).filter(
            Playbook.id == execution_data.playbook_id
        ).first()
        if not playbook:
            raise ValueError("Playbook no encontrado")

        # Crear registro en base de datos
        execution = PlaybookExecution(
            playbook_id=execution_data.playbook_id,
            user_id=1,
            status='pending',
            variables_used=execution_data.variables or {}
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        # Registrar sesión WebSocket
        websocket_manager.start_execution_session(
            session_id, "playbook", execution.id
        )

        # Lanzar ejecución en background
        background_tasks.add_task(
            ExecutionService._run_ansible_streaming,
            execution.id, session_id, playbook.id
        )

        return execution, session_id

    @staticmethod
    async def _run_ansible_streaming(execution_id: int,
                                      session_id: str,
                                      playbook_id: int):
        """Ejecutar playbook Ansible con streaming línea a línea"""
        db = SessionLocal()
        try:
            execution = db.query(PlaybookExecution).filter_by(
                id=execution_id
            ).first()
            playbook = db.query(Playbook).filter_by(
                id=playbook_id
            ).first()

            execution.status = 'running'
            db.commit()
            await update_execution_status(
                session_id, "running", "playbook",
                {"execution_id": execution_id,
                 "playbook_name": playbook.name}
            )

            # Escribir playbook a fichero temporal
            pb_file = os.path.join(
                tempfile.gettempdir(),
                f"playbook_{uuid.uuid4().hex[:12]}.yml"
            )
            with open(pb_file, 'w') as f:
                f.write(playbook.playbook_content)

            # Construir y ejecutar comando Ansible
            cmd = ['ansible-playbook', pb_file, '-i', 'localhost,']
            env = os.environ.copy()
            env['ANSIBLE_FORCE_COLOR'] = 'false'
            # HOST_KEY_CHECKING desactivado: VMs efímeras con host keys
            # que cambian en cada despliegue. No aplicar en producción.
            env['ANSIBLE_HOST_KEY_CHECKING'] = 'false'

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env
            )

            # Streaming línea a línea
            output_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode('utf-8', errors='replace').rstrip()
                output_lines.append(line_str)
                # Emitir cada línea al WebSocket en tiempo real
                await stream_to_websocket(
                    session_id, line_str, "ansible",
                    execution_id=execution_id
                )

            return_code = await process.wait()

            # Persistir resultado
            execution.output_log = '\n'.join(output_lines)
            execution.status = (
                'completed' if return_code == 0 else 'failed'
            )
            execution.completed_at = datetime.utcnow()
            db.commit()

            await update_execution_status(
                session_id, execution.status, "playbook",
                {"execution_id": execution_id,
                 "return_code": return_code}
            )

        except Exception as e:
            # Registrar error en BD y notificar por WebSocket
            await stream_to_websocket(
                session_id, f"Error: {str(e)}", "error",
                execution_id=execution_id
            )
            await update_execution_status(
                session_id, "failed", "playbook",
                {"error": str(e)}
            )
        finally:
            db.close()
