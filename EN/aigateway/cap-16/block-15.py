# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# bcrypt with cost=13 (gateway/app/core/security.py:51-52)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=13,
)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
