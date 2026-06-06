# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Shamir GF(256) — byte by byte (gateway/app/services/key_escrow_service.py)
def shamir_split(secret: bytes, threshold: int, total: int) -> List[bytes]:
    """Splits secret into total shares; any threshold allows reconstruction."""
    if not (1 < threshold <= total <= 255):
        raise ValueError("invalid Shamir parameters")
    shares: List[bytearray] = [bytearray([i + 1]) for i in range(total)]
    for byte in secret:
        coeffs = [byte] + [secrets.randbits(8) for _ in range(threshold - 1)]
        for i in range(total):
            shares[i].append(_gf_eval_poly(coeffs, i + 1))  # Horner in GF(256)
    return [bytes(s) for s in shares]

def shamir_combine(shares: List[bytes]) -> bytes:
    """Reconstructs secret from >=threshold shares (Lagrange GF(256))."""
    # Lagrange interpolation evaluated at 0, byte by byte
    ...
    return bytes(out)
