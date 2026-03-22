# Extraído de: LibroBugBounty/cap-15-token-theft-persistencia.md
# Pseudocódigo de la lógica de evaluación de un EDR
def evaluate_process(process):
    """Decide si un proceso es confiable."""
    # Paso 1: Verificar firma digital
    if process.is_signed and process.signer in TRUSTED_PUBLISHERS:
        trust_score = 80  # Alta confianza base
    else:
        trust_score = 20  # Baja confianza — monitorización intensiva

    # Paso 2: Verificar reputación del path
    if process.path.startswith(KNOWN_INSTALL_DIRS):
        trust_score += 10

    # Paso 3: Verificar comportamiento
    if trust_score >= 70:
        # Monitorización ligera: solo alertas de alta severidad
        monitoring_level = "LOW"
    else:
        # Monitorización intensiva: cada syscall registrado
        monitoring_level = "HIGH"

    return trust_score, monitoring_level
