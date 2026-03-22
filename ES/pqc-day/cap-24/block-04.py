# Extraído de: LibroPQC/cap-24-saas.md
class UpgradePlanResource(Resource):
    """Actualización de plan de suscripción."""

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        # Solo el propietario puede cambiar el plan
        if user.role != 'org_owner':
            return {'error': 'Solo el propietario puede cambiar '
                             'el plan'}, 403

        data = request.get_json()
        new_plan = data.get('plan')

        valid_plans = ['free', 'starter', 'professional', 'enterprise']
        if new_plan not in valid_plans:
            return {'error': f'Plan no válido: {new_plan}'}, 400

        org = Organization.query.get(user.organization_id)

        # Definir límites por plan
        plan_limits = {
            'free':         {'clients': 1,    'users': 1,  'analyses': 5},
            'starter':      {'clients': 3,    'users': 2,  'analyses': 20},
            'professional': {'clients': 10,   'users': 10, 'analyses': 100},
            'enterprise':   {'clients': 9999, 'users': 50, 'analyses': 99999}
        }

        limits = plan_limits[new_plan]

        # Verificar que el downgrade no viola los datos existentes
        if new_plan != 'enterprise':
            current_clients = Client.query.filter_by(
                organization_id=org.id, status='active'
            ).count()
            current_users = User.query.filter_by(
                organization_id=org.id, is_active=True
            ).count()

            if current_clients > limits['clients']:
                return {
                    'error': f'No puedes cambiar a {new_plan}: '
                             f'tienes {current_clients} clientes activos '
                             f'y el plan permite {limits["clients"]}.'
                }, 409

            if current_users > limits['users']:
                return {
                    'error': f'No puedes cambiar a {new_plan}: '
                             f'tienes {current_users} usuarios activos '
                             f'y el plan permite {limits["users"]}.'
                }, 409

        # Aplicar cambio
        old_plan = org.subscription_plan
        org.subscription_plan = new_plan
        org.max_clients = limits['clients']
        org.max_users = limits['users']
        org.max_analyses_per_month = limits['analyses']
        org.features = PLAN_FEATURES[new_plan]

        db.session.commit()

        # Registrar en audit log
        _log_plan_change(org.id, user.id,
                        old_plan, new_plan)

        return {
            'message': f'Plan actualizado a {new_plan}',
            'organization': org.to_dict()
        }, 200
