# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
def full_ioctl_assessment(driver_path, device_path):
    """Evaluación completa de IOCTLs de un driver."""
    # Fase 1: Descubrimiento estático (Docker)
    ioctls = scan_for_ioctls(driver_path)
    neither = {c for c in ioctls if (c & 0x3) == 3}
    buffered = {c for c in ioctls if (c & 0x3) == 0}

    print(f"[*] {len(ioctls)} IOCTLs encontrados")
    print(f"    {len(neither)} METHOD_NEITHER (CRITICAL)")
    print(f"    {len(buffered)} METHOD_BUFFERED")

    # Fase 2: Probing de dispositivo (Windows)
    handle = open_device(device_path)
    if not handle:
        print("[-] Dispositivo no accesible — bypass DACL necesario")
        return

    # Fase 3: Fuzzing (prioridad: NEITHER > DIRECT > BUFFERED)
    for code in sorted(neither):
        print(f"\n[*] Fuzzing METHOD_NEITHER: {hex(code)}")
        for size in [0, 4, 8, 16, 32, 64, 256, 4096]:
            buf = b"\x41" * size
            ok, err, out, ret = send_ioctl(handle, code, buf, size)
            status = "OK" if ok else f"err={err}"
            print(f"  size={size:4d}: {status}, ret={ret}B")

    for code in sorted(buffered):
        print(f"\n[*] Fuzzing METHOD_BUFFERED: {hex(code)}")
        for size in [0, 16, 256]:
            buf = b"\x00" * size
            ok, err, out, ret = send_ioctl(handle, code, buf, size)
            status = "OK" if ok else f"err={err}"
            print(f"  size={size:4d}: {status}, ret={ret}B")
