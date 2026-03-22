# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
def check_pe_security(pe):
    """Verifica mitigaciones del compilador en el PE."""
    dll_chars = pe.OPTIONAL_HEADER.DllCharacteristics
    features = {
        "ASLR":              bool(dll_chars & 0x0040),
        "DEP/NX":            bool(dll_chars & 0x0100),
        "No SEH":            bool(dll_chars & 0x0400),
        "CFG":               bool(dll_chars & 0x4000),
        "Force Integrity":   bool(dll_chars & 0x0080),
        "High Entropy ASLR": bool(dll_chars & 0x0020),
    }

    # Análisis de entropía por sección (detecta packing)
    for section in pe.sections:
        name = section.Name.decode().rstrip('\x00')
        entropy = section.get_entropy()
        # Entropía > 7.0 sugiere código empaquetado o cifrado
        # Entropía < 1.0 sugiere sección vacía o padding
        features[f"entropy_{name}"] = round(entropy, 2)

    return features
