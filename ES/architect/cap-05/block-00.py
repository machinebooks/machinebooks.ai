# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
# Configuración de múltiples schemas en Flask
# Credenciales desde variables de entorno — nunca hardcodeadas
# Conexiones con TLS obligatorio (require_secure_transport en MySQL)
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASSWORD']
DB_HOST = os.environ.get('DB_HOST', 'db')

# El bind por defecto recibe los modelos sin __bind_key__ explícito
SQLALCHEMY_DATABASE_URI = (
    f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/operations_db'
    '?charset=utf8mb4'
)

SQLALCHEMY_BINDS = {
    'platform_core': (
        f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/platform_core'
        '?charset=utf8mb4'
    ),
    'analytics_db': (
        f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/analytics_db'
        '?charset=utf8mb4'
    ),
}

# Connection pooling[^c05-connection-pooling] para manejar carga de Celery workers y API concurrente
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 50,          # Conexiones base por pool
    'max_overflow': 100,      # Conexiones extra bajo pico de carga
    'pool_pre_ping': True,    # Verifica conexión antes de usarla (evita "MySQL has gone away")
    'pool_recycle': 3600,     # Recicla conexiones cada hora (evita timeouts de inactividad)
    'pool_timeout': 30,       # Tiempo máximo esperando una conexión del pool
}
