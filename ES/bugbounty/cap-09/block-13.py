# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
def fuzz_port_io_ioctl(handle, read_code, write_code):
    """Fuzz IOCTLs de lectura/escritura de puertos I/O."""
    # Puertos interesantes para probar
    test_ports = [
        (0x61, "PIT Speaker"),
        (0x70, "CMOS/RTC Address"),
        (0x71, "CMOS/RTC Data"),
        (0xCF8, "PCI Config Address"),
        (0xCFC, "PCI Config Data"),
    ]

    for port, description in test_ports:
        buf = struct.pack("<HH", port, 0)  # port + padding
        ok, err, out, ret = send_ioctl(handle, read_code, buf, len(buf))
        if ok and ret >= 1:
            value = out[0]
            print(f"[+] Port 0x{port:X} ({description}): 0x{value:02X}")
        else:
            print(f"[-] Port 0x{port:X}: err={err}")
