# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/api/clients.py — RBAC explícito + aislamiento
class ClientResource(Resource):
    @jwt_required()
    def delete(self, client_id):
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        # 1. Verificación de rol: solo owner y admin pueden eliminar
        if user.role not in ['org_owner', 'org_admin']:
            return {'error': 'Permisos insuficientes'}, 403

        client = Client.query.get(client_id)

        # 2. Verificación de aislamiento: el cliente debe pertenecer
        #    a la misma organización que el usuario
        if not client or client.organization_id != user.organization_id:
            return {'error': 'Cliente no encontrado'}, 404

        # Borrado lógico: archivar, no eliminar
        client.status = 'archived'
        db.session.commit()

        return {'message': 'Cliente archivado'}, 200
