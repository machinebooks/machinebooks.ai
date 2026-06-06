# Extraído de: LibroAIGateway/cap-32-modelo-de-datos.md
# Versión del esquema de hashing:
#   v1 = SHA-256(prompt) sin salt — legacy, vulnerable.
#   v2 = SHA-256(org.audit_salt + ":" + prompt) — actual.
hash_version = Column(String(4), nullable=False, default="v2", server_default="v2")
