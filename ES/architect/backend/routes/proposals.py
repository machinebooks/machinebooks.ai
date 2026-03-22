# Extraído de: LibroTecnico/cap-07-api-rest.md
# backend/routes/proposals.py
from flask import Blueprint, request, jsonify, g
from middleware.auth import platform_guard, require_permission
from middleware.rate_limit import rate_limit
from models.operations import Proposal, ProposalType
from services.proposal_service import ProposalService
from exceptions import ValidationError  # o marshmallow.exceptions
import structlog

logger = structlog.get_logger()

# Definición del blueprint con prefijo de URL
proposals_bp = Blueprint('proposals', __name__, url_prefix='/api/proposals')

@proposals_bp.route('/', methods=['GET'])
@platform_guard
@require_permission('proposals', 'read')
@rate_limit(max_requests=60, window_seconds=60, key_prefix="proposals_list")
def list_proposals():
    """Lista propuestas con filtros y paginación.
    Devuelve solo las propuestas accesibles para el usuario actual."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status')

    try:
        query = Proposal.query.filter_by(is_active=True)

        # Filtro por estado si se especifica
        if status:
            query = query.filter_by(status=status)

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'proposals': [p.to_dict() for p in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        })
    except Exception as e:
        logger.error("proposals_list_failed",
                     request_id=g.request_id,
                     error=str(e))
        return jsonify({'error': 'Error al obtener propuestas'}), 500


@proposals_bp.route('/', methods=['POST'])
@platform_guard
@require_permission('proposals', 'write')
@rate_limit(max_requests=10, window_seconds=60, key_prefix="proposals_create")
def create_proposal():
    """Crea una nueva propuesta. Límite más estricto por ser operación de escritura."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos de propuesta requeridos'}), 400

    # Validación básica — las reglas de negocio van en el service
    required_fields = ['client_id', 'title', 'proposal_type']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({'error': f'Campos requeridos: {", ".join(missing)}'}), 400

    try:
        proposal = ProposalService.create(data, created_by=g.current_user.id)
        logger.info("proposal_created",
                    request_id=g.request_id,
                    proposal_id=proposal.id,
                    user_id=g.current_user.id)
        return jsonify(proposal.to_dict()), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error("proposal_create_failed",
                     request_id=g.request_id,
                     error=str(e))
        return jsonify({'error': 'Error al crear propuesta'}), 500
