# Extraído de: LibroCISO/cap-03-ecosistema-tecnico.md
# Variables representativas — 130+ variables adicionales en .env.example

# === Seguridad (las más críticas) ===
JWT_ALGORITHM=RS256              # HS256 solo en desarrollo local
ENCRYPTION_KEY=<CLAVE_AES_256>   # AES-256-GCM para datos sensibles en reposo
PKI_ENABLED=true                 # mTLS bidireccional en producción
MFA_REQUIRED_ROLES=admin,auditor,dpo  # TOTP obligatorio para roles privilegiados

# === Autenticación ===
AUTH_BACKEND=jwt                 # jwt | ldap | saml | pki

# === IA — multi-proveedor ===
AI_PROVIDER=anthropic            # anthropic | azure_openai | openai | ollama
ANTHROPIC_API_KEY=<set-in-vault>
AI_FALLBACK_CHAIN=anthropic,azure_openai,ollama  # Orden de fallback
OLLAMA_BASE_URL=http://ollama:11434  # Fallback local para entornos sin internet

# === Módulos licenciados ===
LICENSED_MODULES=privacy,risk,compliance,ai,ens,iso27001
# Cada módulo es un gate técnico: si no está licenciado, la API devuelve 403
