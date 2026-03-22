# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/api/auth.py — Registro con creación atómica de organización
class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        # Validación de campos obligatorios
        required = ['organization_name', 'email', 'password', 'full_name']
        for field in required:
            if field not in data:
                return {'error': f'Campo obligatorio: {field}'}, 400

        # Validación de formato de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return {'error': 'Formato de email inválido'}, 400

        # Política de contraseñas: mínimo 8 caracteres
        if len(data['password']) < 8:
            return {'error': 'La contraseña debe tener al menos 8 caracteres'}, 400

        # Unicidad de email
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email ya registrado'}, 409

        try:
            # Crear organización con slug único
            org = Organization(
                name=data['organization_name'],
                slug=generate_unique_slug(data['organization_name']),
                subscription_plan='free',
                billing_email=data['email']
            )
            db.session.add(org)
            db.session.flush()  # Obtener org.id sin commit

            # Crear usuario propietario con bcrypt
            user = User(
                organization_id=org.id,
                email=data['email'],
                password_hash=bcrypt.hash(data['password']),
                full_name=data['full_name'],
                role='org_owner',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

            # Tokens JWT con identidad como string
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(),
                'organization': org.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error de registro: {e}', exc_info=True)
            # NUNCA exponer str(e) al cliente: puede filtrar
            # rutas internas, estado de la BD o datos sensibles.
            return {'error': 'Error interno de registro'}, 500
