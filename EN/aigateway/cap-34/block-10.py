# Extracted from: LibroAIGateway/cap-34-celery-deployment-config.md
def validate_security(self) -> None:
    """Blocks startup if there is insecure configuration in production."""
    if self.is_production and not self.N7X_MASTER_KEY:
        raise ValueError("N7X_MASTER_KEY is required in production.")
    if self.is_production:
        pseudonym_salt = os.environ.get("N7X_PSEUDONYM_SALT")
        if not pseudonym_salt or len(pseudonym_salt) < 32:
            raise ValueError("N7X_PSEUDONYM_SALT is required (>=32 chars).")
    if self.is_production and "://root:" in (self.DATABASE_URL or ""):
        raise ValueError("DATABASE_URL cannot use 'root' in production.")
