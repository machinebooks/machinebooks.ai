# Extraído de: LibroPQC/cap-22-celery.md
@celery_app.task(name='health_check_task')
def health_check_task():
    """Tarea trivial para verificar que el worker responde."""
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}


class CeleryStatusResource(Resource):
    @require_auth
    @require_role('admin')
    def get(self):
        """Estado operativo de Celery para el panel admin."""
        inspector = celery_app.control.inspect()

        # Tareas activas (en ejecución ahora)
        active = inspector.active() or {}
        # Tareas reservadas (asignadas pero no ejecutándose)
        reserved = inspector.reserved() or {}
        # Estadísticas del worker
        stats = inspector.stats() or {}

        total_active = sum(len(tasks) for tasks in active.values())
        total_reserved = sum(len(tasks) for tasks in reserved.values())

        # Longitud de cada cola (consulta directa a Redis)
        queue_lengths = {}
        for queue_name in ['repository_analysis', 'certificate_scanning',
                           'cloud_audit', 'ai_analysis']:
            length = redis_client.llen(queue_name)
            queue_lengths[queue_name] = length

        return {
            'workers_online': len(stats),
            'active_tasks': total_active,
            'reserved_tasks': total_reserved,
            'queue_lengths': queue_lengths,
            'worker_details': {
                name: {
                    'active': len(active.get(name, [])),
                    'uptime': data.get('uptime', 0),
                    'processed': data.get('total', {}).get(
                        'tasks.analyze_repository_task', 0
                    )
                }
                for name, data in stats.items()
            }
        }, 200
