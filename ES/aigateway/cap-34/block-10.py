# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
def validate_security(self) -> None:
    """Bloquea el arranque si hay configuración insegura en producción."""
    if self.is_production and not self.N7X_MASTER_KEY:
        raise ValueError("N7X_MASTER_KEY es obligatoria en producción.")
    if self.is_production:
        pseudonym_salt = os.environ.get("N7X_PSEUDONYM_SALT")
        if not pseudonym_salt or len(pseudonym_salt) < 32:
            raise ValueError("N7X_PSEUDONYM_SALT es obligatoria (>=32 chars).")
    if self.is_production and "://root:" in (self.DATABASE_URL or ""):
        raise ValueError("DATABASE_URL no puede usar 'root' en producción.")
