# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
@staticmethod
def _pick_weighted(rows):
    """Random weighted por weight. Si todos pesan igual, equiprobable."""
    weights = [max(1, int(d.weight or 1)) for d in rows]
    return random.choices(rows, weights=weights, k=1)[0]
