# Extraído de: LibroPQC/cap-21-docker.md
# .env.example — Variables de entorno para la Plataforma PQC
# Copiar a .env y rellenar con valores reales
# NUNCA versionar el fichero .env en git

# --- MySQL ---
MYSQL_ROOT_PASSWORD=<TU_PASSWORD_ROOT>
MYSQL_DATABASE=pqc_db
MYSQL_USER=pqc_user
MYSQL_PASSWORD=<TU_PASSWORD_MYSQL>
MYSQL_PORT=3306

# --- Redis ---
REDIS_PORT=6379

# --- Backend Flask ---
FLASK_APP=app
FLASK_ENV=development           # development | production
JWT_SECRET_KEY=<TU_SECRET_KEY>  # Mínimo 32 caracteres aleatorios
LOG_LEVEL=INFO
BACKEND_PORT=5000
GUNICORN_WORKERS=4              # Regla: 2 * num_cpus + 1

# --- Celery ---
CELERY_CONCURRENCY=2

# --- IA (Claude API) ---
ANTHROPIC_API_KEY=<set-in-vault>

# --- Frontend ---
FRONTEND_PORT=3000
VITE_API_URL=/api
VITE_WS_URL=ws://localhost:8080

# --- Nginx ---
NGINX_PORT=8080
