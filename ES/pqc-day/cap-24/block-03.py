# Extraído de: LibroPQC/cap-24-saas.md
class RegisterResource(Resource):
    """Registro: crea organización + usuario propietario en una sola operación."""

    def post(self):
        data = request.get_json()

        # Validaciones básicas
        required = ['organization_name', 'email', 'password', 'full_name']
        for field in required:
            if field not in data:
                return {'error': f'Campo requerido: {field}'}, 400

        if len(data['password']) < 8:
            return {'error': 'La contraseña debe tener al menos '
                             '8 caracteres'}, 400

        # Comprobar email duplicado
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'El correo ya está registrado'}, 409

        try:
            # 1. Crear organización con plan Free
            slug = _generate_slug(data['organization_name'])
            organization = Organization(
                name=data['organization_name'],
                slug=slug,
                subscription_plan='free',
                max_clients=1,
                max_users=1,
                max_analyses_per_month=5,
                features=PLAN_FEATURES['free'],  # Features del plan Free
                billing_email=data['email']
            )
            db.session.add(organization)
            db.session.flush()  # Obtener ID antes de crear usuario

            # 2. Crear usuario propietario
            user = User(
                organization_id=organization.id,
                email=data['email'],
                password_hash=bcrypt.hash(data['password']),
                full_name=data['full_name'],
                role='org_owner',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

            # 3. Generar tokens JWT
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                'message': 'Registro completado',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(),
                'organization': organization.to_dict(),
                'next_step': 'create_client'  # Guía para el frontend
            }, 201

        except Exception as e:
            db.session.rollback()
            # No exponer detalles internos de la excepción al cliente:
            # str(e) puede filtrar rutas, nombres de tabla o stack traces
            logger.error(f'Error en registro: {e}')
            return {'error': 'Error interno en el registro. '
                             'Inténtelo de nuevo o contacte soporte.'}, 500
