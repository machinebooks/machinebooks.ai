# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
def fuzz_ioctl_sequences(handle):
    """Prueba secuencias de IOCTLs que pueden revelar state bugs."""
    MAP = 0x222400
    UNMAP = 0x222404

    # Secuencia 1: Double map (mismo rango)
    buf = struct.pack("<QII", 0x1000, 0x1000, 0)
    send_ioctl(handle, MAP, buf, 16)
    send_ioctl(handle, MAP, buf, 16)  # ¿Double map?

    # Secuencia 2: Unmap sin map previo
    send_ioctl(handle, UNMAP, buf, 16)  # ¿Crash?

    # Secuencia 3: Map → Unmap → Map → Unmap (stress)
    for _ in range(1000):
        send_ioctl(handle, MAP, buf, 16)
        send_ioctl(handle, UNMAP, buf, 16)

    # Secuencia 4: Múltiples maps sin unmap (resource leak)
    for addr in range(0x1000, 0x100000, 0x1000):
        buf = struct.pack("<QII", addr, 0x1000, 0)
        ok, err, _, _ = send_ioctl(handle, MAP, buf, 16)
        if not ok:
            print(f"Map failed at 0x{addr:X} after {(addr-0x1000)//0x1000} maps")
            break
