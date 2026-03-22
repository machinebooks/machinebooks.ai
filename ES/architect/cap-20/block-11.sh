# Extraído de: LibroTecnico/cap-20-docker.md
# Ejemplo didáctico: patrones/config/env.example
# ==========================================================
# CONFIGURACIÓN DE LA PLATAFORMA — .env.example
# Copiar a .env y completar con valores reales
# NUNCA subir .env al repositorio (está en .gitignore)
# ==========================================================

# --- BASE DE DATOS ---
MYSQL_ROOT_PASSWORD=<contraseña-segura-generada>
MYSQL_OPS_USER=ops_user
MYSQL_OPS_PASSWORD=<contraseña-única-por-schema>
MYSQL_CORE_USER=core_user
MYSQL_CORE_PASSWORD=<contraseña-única-por-schema>
MYSQL_ANALYTICS_USER=analytics_user
MYSQL_ANALYTICS_PASSWORD=<contraseña-única-por-schema>

# URLs de conexión (usadas por SQLAlchemy en el backend)
DATABASE_URL_OPS=mysql+pymysql://ops_user:<pwd>@mysql_ops:3306/operations_db
DATABASE_URL_CORE=mysql+pymysql://core_user:<pwd>@mysql_core:3306/platform_core
DATABASE_URL_ANALYTICS=mysql+pymysql://analytics_user:<pwd>@mysql_analytics:3306/analytics_db

