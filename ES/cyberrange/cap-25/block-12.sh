# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/config/env-reference.sh

# --- MySQL ---
MYSQL_ROOT_PASSWORD=<contraseña_segura>
MYSQL_DATABASE=CYBERRANGEDB
MYSQL_USER=cyberadmin
MYSQL_PASSWORD=<contraseña_segura>

# --- JWT (obligatorio: la aplicación no arranca sin JWT_SECRET) ---
JWT_SECRET=<secret_aleatorio_de_256_bits>
JWT_EXP_HOURS=4

# --- Redis ---
REDIS_PASSWORD=<contraseña_redis_segura>

# --- Proxmox (conexión principal) ---
PROXMOX_HOST=proxmox.local
PROXMOX_PORT=8006
PROXMOX_TOKEN_ID=cyberrange@pve!api_token   # Token para operaciones de gestión
PROXMOX_TOKEN_SECRET=<uuid_del_token>
PROXMOX_TOKEN_VNC_ID=cyberrange@pve!vnc_token # Token separado para consolas
PROXMOX_TOKEN_VNC_SECRET=<uuid_del_token_vnc>
PROXMOX_SSL_VERIFY=true

# --- Sincronización ---
PROXMOX_SYNC_INTERVAL=15                 # Minutos entre sincronizaciones
PROXMOX_AUTO_CLEANUP_SNAPSHOTS=true
PROXMOX_SNAPSHOT_RETENTION_DAYS=7

# --- Pools y workzones ---
PROXMOX_POOL_PREFIX=cyberrange
MAX_WORKZONES=16
WORKZONE_NETWORK_BASE=10.0.0.0/8

# --- Seguridad ---
PASSWORD_MIN_LENGTH=12
MAX_FAILED_LOGINS=5
ACCOUNT_LOCKOUT_MINUTES=30
SESSION_TIMEOUT_MINUTES=60
MFA_ISSUER=Cyberrange

# --- IA (obligatorio si se activa el módulo de IA) ---
# AI_PROVIDER=claude
# AI_MODEL=claude-sonnet-4-20250514
# ANTHROPIC_API_KEY=<tu_api_key>       # RuntimeError si se activa IA sin esta clave
