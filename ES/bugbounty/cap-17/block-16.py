# Extraído de: LibroBugBounty/cap-17-poc-impacto.md
# Convertir payload.exe a array C
def exe_to_c_array(exe_path, var_name="payload_exe"):
    """Convierte un EXE a un array de bytes C."""
    with open(exe_path, "rb") as f:
        data = f.read()

    lines = []
    lines.append(f"const unsigned char {var_name}[] = {{")
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_bytes = ", ".join(f"0x{b:02x}" for b in chunk)
        lines.append(f"    {hex_bytes},")
    lines.append("};")
    lines.append(f"const unsigned int {var_name}_len = {len(data)};")

    return "\n".join(lines)

# Uso
c_array = exe_to_c_array("payload_service.exe")
# Pegar el output en epic_lpe_exploit.c
