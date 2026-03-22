# Extraído de: LibroBugBounty/cap-14-extension-tampering.md
import os
import hashlib
from pathlib import Path

def find_copilot_extension():
    """Localiza la extensión de Copilot Chat en VS Code."""
    ext_dir = Path.home() / ".vscode" / "extensions"
    for d in ext_dir.iterdir():
        if d.name.startswith("github.copilot-chat"):
            ext_js = d / "dist" / "extension.js"
            if ext_js.exists():
                return ext_js
    return None

def verify_integrity(ext_js):
    """Verifica si VS Code detecta modificaciones."""
    # Hash original
    original = ext_js.read_bytes()
    original_hash = hashlib.sha256(original).hexdigest()
    print(f"Original hash: {original_hash}")
    print(f"Size: {len(original):,} bytes")

    # Modificar (append inocuo)
    with open(ext_js, 'ab') as f:
        f.write(b'\n// integrity test\n')

    modified = ext_js.read_bytes()
    modified_hash = hashlib.sha256(modified).hexdigest()
    print(f"Modified hash: {modified_hash}")
    print(f"Hashes match: {original_hash == modified_hash}")

    # Resultado: VS Code carga la extensión modificada sin error
    # No hay verificación de firma, hash ni checksum
    return original  # Para restaurar después
