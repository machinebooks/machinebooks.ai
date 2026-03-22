# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
import ctypes
import ctypes.wintypes as wt

kernel32 = ctypes.windll.kernel32

def probe_device_access(device_path):
    """Intenta abrir el dispositivo con múltiples combinaciones."""
    access_flags = [
        ("GENERIC_RW",      0xC0000000),
        ("GENERIC_READ",    0x80000000),
        ("READ_CONTROL",    0x00020000),
        ("SYNCHRONIZE",     0x00100000),
        ("MAXIMUM_ALLOWED", 0x02000000),
        ("ZERO",            0x00000000),
        ("FILE_READ_DATA",  0x00000001),
        ("FILE_WRITE_DATA", 0x00000002),
    ]

    results = []
    for name, flag in access_flags:
        h = kernel32.CreateFileW(
            device_path, flag, 0, None,
            3,     # OPEN_EXISTING
            0x80,  # FILE_ATTRIBUTE_NORMAL
            None
        )
        err = kernel32.GetLastError()
        opened = h and h != ctypes.c_void_p(-1).value
        results.append({
            "access": name, "opened": opened, "error": err,
        })
        if opened:
            kernel32.CloseHandle(h)

    return results
