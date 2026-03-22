# Extraído de: LibroBugBounty/cap-14-extension-tampering.md
def patch_hash(exe_path, old_hash, new_hash):
    """Reemplaza el hash viejo con el nuevo en el ejecutable."""
    data = bytearray(Path(exe_path).read_bytes())
    old_bytes = old_hash.encode('ascii')
    new_bytes = new_hash.encode('ascii')

    idx = data.find(old_bytes)
    if idx == -1:
        raise ValueError(f"Hash {old_hash[:16]}... not found")

    data[idx:idx+64] = new_bytes
    Path(exe_path).write_bytes(bytes(data))
    print(f"Patched at offset {hex(idx)}")
    print(f"  Old: {old_hash[:32]}...")
    print(f"  New: {new_hash[:32]}...")
