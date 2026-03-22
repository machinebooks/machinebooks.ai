# Extraído de: LibroPQC/cap-04-requisito-arquitectura.md
# Ejemplo didáctico: patrones/routes/pqc_analysis/resources.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Client, CryptoFinding
from app.schemas import findings_schema
from functools import wraps

def require_permission(permission):
    """Decorador: verifica que el usuario tiene el permiso requerido."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = User.query.get(get_jwt_identity())
            if not user or not user.has_permission(permission):
                return {"error": "Permisos insuficientes"}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class FindingsResource(Resource):
    """Hallazgos criptográficos — siempre filtrados por organización."""

    @jwt_required()
    @require_permission('view_findings')
    def get(self, client_id=None):
        """Lista hallazgos. Tres niveles de filtrado:
        1. JWT verifica identidad del usuario
        2. organization_id aísla los datos del tenant
        3. client_id opcionalmente filtra por cliente
        """
        user = User.query.get(get_jwt_identity())

        # REGLA CARDINAL: siempre filtrar por organización
        query = CryptoFinding.query.filter_by(
            organization_id=user.organization_id
        )

        # Si es client_user, filtrar además por su cliente
        if user.role == 'client_user':
            query = query.filter_by(client_id=user.client_id)
        elif client_id:
            # Verificar que el cliente pertenece a la organización
            client = Client.query.filter_by(
                id=client_id,
                organization_id=user.organization_id
            ).first()
            if not client:
                return {"error": "Cliente no encontrado"}, 404
            query = query.filter_by(client_id=client_id)

        # Filtros opcionales por query string
        risk_level = request.args.get('risk_level')
        if risk_level:
            query = query.filter_by(risk_level=risk_level)

        pqc_compliant = request.args.get('pqc_compliant')
        if pqc_compliant is not None:
            query = query.filter_by(
                pqc_compliant=pqc_compliant.lower() == 'true'
            )

        findings = query.order_by(
            CryptoFinding.risk_level.desc(),
            CryptoFinding.created_at.desc()
        ).all()

        return findings_schema.dump(findings), 200
