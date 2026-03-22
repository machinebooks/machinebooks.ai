# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/api/auth.py — Login con verificación bcrypt
class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return {'error': 'Email y contraseña requeridos'}, 400

        user = User.query.filter_by(email=data['email']).first()

        # Verificación deliberadamente vaga: no revelar si el email existe
        if not user or not bcrypt.verify(data['password'], user.password_hash):
            return {'error': 'Credenciales inválidas'}, 401

        if not user.is_active:
            return {'error': 'Cuenta desactivada'}, 403

        # Registrar último acceso
        user.last_login = datetime.utcnow()
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'organization': user.organization.to_dict()
        }, 200
