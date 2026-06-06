# Extracted from: LibroAIGateway/cap-32-data-model.md
# Hashing scheme version:
#   v1 = SHA-256(prompt) without salt — legacy, vulnerable.
#   v2 = SHA-256(org.audit_salt + ":" + prompt) — current.
hash_version = Column(String(4), nullable=False, default="v2", server_default="v2")
