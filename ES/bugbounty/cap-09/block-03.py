# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
def analyze_handler_context(filepath, ioctl_locations):
    """Para cada IOCTL, analiza las calls peligrosas cercanas."""
    pe = pefile.PE(str(filepath))
    data = filepath.read_bytes()

    dangerous_funcs = [
        "MmMapIoSpace", "MmCopyMemory", "MmMapLockedPages",
        "ProbeForWrite", "ProbeForRead", "RtlCopyMemory",
    ]
    validation_funcs = [
        "SePrivilegeCheck", "SeSinglePrivilegeCheck", "SeAccessCheck",
    ]

    results = []
    for code, locations in ioctl_locations.items():
        for loc in locations:
            if loc.get("instruction") == "raw_bytes":
                continue
            addr = int(loc["addr"], 16)
            # Desensamblamos 512 bytes alrededor del IOCTL
            context = extract_context_bytes(data, pe, addr, 256)

            found_danger = set()
            found_validation = set()
            for insn in cs.disasm(context, addr - 256):
                if insn.mnemonic == 'call':
                    for df in dangerous_funcs:
                        if df.lower() in insn.op_str.lower():
                            found_danger.add(df)
                    for vf in validation_funcs:
                        if vf.lower() in insn.op_str.lower():
                            found_validation.add(vf)

            if found_danger:
                results.append({
                    "ioctl": hex(code),
                    "danger": list(found_danger),
                    "validation": list(found_validation),
                    "safe": len(found_validation) > 0,
                })
    return results
