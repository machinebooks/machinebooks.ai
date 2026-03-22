# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
ntdll = ctypes.windll.ntdll

def try_nt_open(nt_path, access):
    """Abrir vía NtOpenFile con path NT directo."""
    us = UNICODE_STRING()
    us.Buffer = nt_path
    us.Length = len(nt_path) * 2
    us.MaximumLength = us.Length + 2

    oa = OBJECT_ATTRIBUTES()
    oa.Length = ctypes.sizeof(oa)
    oa.ObjectName = ctypes.pointer(us)
    oa.Attributes = 0x40  # OBJ_CASE_INSENSITIVE

    handle = wt.HANDLE()
    iosb = IO_STATUS_BLOCK()
    status = ntdll.NtOpenFile(
        ctypes.byref(handle), access,
        ctypes.byref(oa), ctypes.byref(iosb),
        3, 0  # FILE_SHARE_READ | FILE_SHARE_WRITE
    )
    return (handle.value, 0) if status == 0 else (None, status)
