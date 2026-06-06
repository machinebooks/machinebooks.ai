# Extraído de: LibroAIGateway/cap-25-mcp-registro-catalogo.md
def to_dict(self, include_secrets: bool = False):
    d = {
        "id": self.id,
        "slug": self.slug,
        "name": self.name,
        "transport": self.transport,
        "auth_type": self.auth_type,
        "scope": self.scope,
        "is_enabled": bool(self.is_enabled),
        # ... resto de campos no sensibles
    }
    if include_secrets:
        d["env"] = self.env
        d["headers"] = self.headers
        d["auth_secret_ref"] = self.auth_secret_ref
    return d
