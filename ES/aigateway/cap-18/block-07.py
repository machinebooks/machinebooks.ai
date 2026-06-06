# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Shamir GF(256) — byte a byte (gateway/app/services/key_escrow_service.py)
def shamir_split(secret: bytes, threshold: int, total: int) -> List[bytes]:
    """Divide secret en total shares; cualquier threshold permite reconstruir."""
    if not (1 < threshold <= total <= 255):
        raise ValueError("invalid Shamir parameters")
    shares: List[bytearray] = [bytearray([i + 1]) for i in range(total)]
    for byte in secret:
        coeffs = [byte] + [secrets.randbits(8) for _ in range(threshold - 1)]
        for i in range(total):
            shares[i].append(_gf_eval_poly(coeffs, i + 1))  # Horner en GF(256)
    return [bytes(s) for s in shares]

def shamir_combine(shares: List[bytes]) -> bytes:
    """Reconstruye secret a partir de >=threshold shares (Lagrange GF(256))."""
    # Interpolación de Lagrange evaluada en 0, byte a byte
    ...
    return bytes(out)
