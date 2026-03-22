# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
def intelligent_mutation(handle, ioctl_code=0x222400):
    """Mutación guiada por la semántica de MmMapIoSpace."""

    # Grupo 1: Explorar rangos de dirección física
    # El espacio de direcciones físicas de un PC típico:
    # 0x00000000 - 0x000FFFFF: legacy (real mode, BIOS)
    # 0x00100000 - 0x3FFFFFFF: RAM principal (~1 GB)
    # 0xF0000000 - 0xFFFFFFFF: MMIO de dispositivos PCI
    interesting_addrs = [
        0x00000000,  # Página cero — null page
        0x000B8000,  # VGA text buffer (legacy)
        0x000F0000,  # BIOS ROM
        0x00100000,  # Inicio de RAM convencional
        0xFED00000,  # HPET (High Precision Event Timer)
        0xFEE00000,  # Local APIC
        0xF0000000,  # Inicio de MMIO PCI típico
    ]

    for addr in interesting_addrs:
        buf = struct.pack("<QII", addr, 0x1000, 0)
        ok, err, out, ret = send_ioctl(handle, ioctl_code, buf, 16)
        if ok and ret >= 8:
            virt = struct.unpack("<Q", out[:8])[0]
            print(f"[+] Phys 0x{addr:08X} -> Virt 0x{virt:016X}")
        else:
            print(f"[-] Phys 0x{addr:08X}: err={err}")

    # Grupo 2: Explorar tamaños de mapeo
    # ¿Hay un límite máximo? ¿El driver valida el tamaño?
    for size_exp in range(12, 32):  # 4 KB a 4 GB
        size = 1 << size_exp
        buf = struct.pack("<QII", 0x1000, size, 0)
        ok, err, out, ret = send_ioctl(handle, ioctl_code, buf, 16)
        status = "OK" if ok else f"err={err}"
        print(f"  Size 0x{size:08X} ({size//1024} KB): {status}")
        if not ok:
            print(f"  [*] Maximum size: 0x{1 << (size_exp-1):08X}")
            break

    # Grupo 3: Explorar tipos de caché
    # MmNonCached=0, MmCached=1, MmWriteCombined=2
    for cache in range(4):
        buf = struct.pack("<QII", 0x1000, 0x1000, cache)
        ok, err, out, ret = send_ioctl(handle, ioctl_code, buf, 16)
        cache_names = {0: "NonCached", 1: "Cached", 2: "WriteCombined"}
        name = cache_names.get(cache, f"Unknown({cache})")
        status = "OK" if ok else f"err={err}"
        print(f"  Cache {name}: {status}")
