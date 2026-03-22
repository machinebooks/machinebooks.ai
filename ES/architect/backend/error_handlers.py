# Extraído de: LibroTecnico/cap-07-api-rest.md
# backend/error_handlers.py
from flask import jsonify, g
import structlog

logger = structlog.get_logger()

def register_error_handlers(app):
    """Registra manejadores de errores globales para respuestas JSON consistentes."""

    @app.errorhandler(400)
    def bad_request(error):
        # No exponer str(error) al cliente — puede filtrar detalles internos
        app.logger.warning("Bad request: %s", error)
        return jsonify({'error': 'Petición incorrecta'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Autenticación requerida'}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Acceso no autorizado'}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({'error': 'Demasiadas peticiones. Intenta más tarde.'}), 429

    @app.errorhandler(500)
    def internal_error(error):
        # El error interno se registra en el log pero nunca se expone al cliente
        request_id = getattr(g, 'request_id', 'unknown')
        logger.error("unhandled_exception",
                     request_id=request_id,
                     error=str(error),
                     error_type=type(error).__name__)
        return jsonify({'error': 'Error interno del servidor'}), 500

    @app.errorhandler(ValidationError)
    def validation_error(error):
        # Las ValidationError de dominio tienen mensajes seguros para mostrar al cliente
        return jsonify({'error': str(error), 'type': 'validation'}), 422
