# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
def extract_driver_strings(filepath):
    """Extrae strings de interés: dispositivos, rutas, PDB."""
    data = filepath.read_bytes()
    interesting = []

    # Buscar strings wide (UTF-16LE) — el estándar en drivers Windows
    i = 0
    while i < len(data) - 1:
        if 0x20 <= data[i] < 0x7f and data[i+1] == 0:
            s = b""
            j = i
            while j < len(data) - 1 and 0x20 <= data[j] < 0x7f and data[j+1] == 0:
                s += bytes([data[j]])
                j += 2
            decoded = s.decode('ascii', errors='ignore')
            if any(p in decoded.lower() for p in [
                '\\device\\', '\\dosdevices\\', 'physical',
                'memory', 'port', 'msr', '.sys', '.pdb'
            ]):
                interesting.append(decoded)
            i = j
        else:
            i += 1

    return list(set(interesting))
