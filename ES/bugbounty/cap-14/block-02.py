# Extraído de: LibroBugBounty/cap-14-extension-tampering.md
import struct

def find_asar_hash_in_exe(exe_path):
    """Busca el hash SHA-256 del ASAR en el ejecutable de Wand."""
    data = Path(exe_path).read_bytes()

    # Buscar strings de 64 caracteres hexadecimales (SHA-256)
    import re
    pattern = re.compile(rb'[0-9a-f]{64}')
    matches = list(pattern.finditer(data))

    candidates = []
    for match in matches:
        hex_str = match.group().decode('ascii')
        offset = match.start()
        # Verificar que no está en una sección de datos conocida
        candidates.append({
            "hash": hex_str,
            "offset": offset,
            "offset_hex": hex(offset),
        })

    return candidates

def patch_hash(exe_path, old_hash, new_hash):
    """Parchea el hash en el ejecutable."""
    data = bytearray(Path(exe_path).read_bytes())
    old_bytes = old_hash.encode('ascii')
    new_bytes = new_hash.encode('ascii')

    idx = data.find(old_bytes)
    if idx >= 0:
        data[idx:idx+64] = new_bytes
        Path(exe_path).write_bytes(bytes(data))
        print(f"[+] Hash patched at offset {hex(idx)}")
        return True
    return False
