# Extraído de: LibroTecnico/cap-07-api-rest.md
# backend/app.py
from flask import Flask
from config import get_config

def create_app(config_name: str = 'production') -> Flask:
    """Fábrica de aplicación Flask. Registra todos los blueprints
    y middleware de forma centralizada."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Middleware de contexto de petición (se aplica a todas las rutas)
    from middleware.request_context import init_request_context
    from middleware.security_headers import init_security_headers
    init_request_context(app)
    init_security_headers(app)

    # Registrar los 22 blueprints por dominio funcional
    from routes.auth import auth_bp
    from routes.clients import clients_bp
    from routes.proposals import proposals_bp
    from routes.documents import documents_bp
    from routes.opportunities import opportunities_bp
    from routes.copilot import copilot_bp
    from routes.cvs import cvs_bp
    from routes.alerts import alerts_bp
    from routes.notifications import notifications_bp
    from routes.admin import admin_bp
    from routes.llm_admin import llm_admin_bp
    # ... (resto de blueprints)

    blueprints = [
        auth_bp, clients_bp, proposals_bp, documents_bp,
        opportunities_bp, copilot_bp, cvs_bp, alerts_bp,
        notifications_bp, admin_bp, llm_admin_bp,
        # ...
    ]
    for bp in blueprints:
        app.register_blueprint(bp)

    # Manejadores de errores globales
    register_error_handlers(app)

    return app
