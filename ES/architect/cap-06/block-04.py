# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
@proposals_bp.route('/api/proposals', methods=['POST'])
@platform_guard                           # Capa 1: JWT válido, claims extraídos
@require_permission('proposals', 'write') # Capa 2: rol tiene permiso de escritura
@rate_limit(limit=30, period=60, scope="user")  # Capa 3: 30 req/min (sliding window, Redis)
def create_proposal():
    """Crear propuesta — requiere permiso de escritura en módulo proposals."""
    # g.current_user_id, g.app_code y g.user_role están disponibles
    data = request.get_json()
    # ... lógica de negocio
