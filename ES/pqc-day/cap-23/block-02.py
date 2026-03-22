# Extraído de: LibroPQC/cap-23-observabilidad.md
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.audit import AuditLog


@clients_bp.route('/clients', methods=['POST'])
@jwt_required()
def create_client():
    """Crear un nuevo cliente con registro de auditoría."""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Lógica de negocio: crear el cliente
    new_client = Client(
        name=data['name'],
        organization_id=current_user.organization_id
    )
    db.session.add(new_client)
    db.session.commit()

    # Registro de auditoría: quién, qué, sobre qué, desde dónde
    AuditLog.log(
        user_id=user_id,
        action='create_client',
        entity_type='client',
        entity_id=new_client.id,
        details={
            'client_name': new_client.name,
            'organization_id': new_client.organization_id
        },
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    return jsonify({'data': new_client.to_dict()}), 201
