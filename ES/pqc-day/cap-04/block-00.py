# Extraído de: LibroPQC/cap-04-requisito-arquitectura.md
# Ejemplo didáctico: patrones/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    """Factory de la aplicación Flask.

    Cada extensión se inicializa con init_app() para
    permitir tests independientes con configuraciones
    distintas.
    """
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Extensiones — orden importa para dependencias
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config['REDIS_URL'],
        default_limits=["200 per hour"]
    )

    # 7 Blueprints — cada módulo es independiente
    from .routes.auth import api_bp
    from .routes.pqc_analysis import pqc_analysis_bp
    from .routes.cloud import cloud_bp
    from .routes.ai_service import ai_bp
    from .routes.compliance import compliance_bp
    from .routes.audit import audit_bp
    from .routes.ai_admin import ai_admin_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(pqc_analysis_bp, url_prefix='/api/v1/pqc-analysis')
    app.register_blueprint(cloud_bp, url_prefix='/api/cloud')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')
    app.register_blueprint(ai_admin_bp, url_prefix='/api/ai-admin')

    # Callback JWT: cargar usuario con organización
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    return app
