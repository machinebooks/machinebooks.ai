# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/config.py — Separación de secretos
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY',
                           'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY',
                               'jwt-secret-key-change-in-production')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY',
                               'encryption-key-32-chars-min!!!')

    # Tokens JWT
    JWT_ACCESS_TOKEN_EXPIRES = 3600      # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 días

class ProductionConfig(Config):
    # En producción: secretos obligatorios desde variables de entorno
    # Si no están definidos, la aplicación no arranca (None fuerza error)
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
