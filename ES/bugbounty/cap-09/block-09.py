# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
def correlate_crash(checkpoint_file, minidump_dir):
    """Correlaciona el último BSOD con el IOCTL que lo causó."""
    import json, os, glob

    with open(checkpoint_file) as f:
        state = json.load(f)

    # Encontrar el minidump más reciente
    dumps = sorted(glob.glob(os.path.join(minidump_dir, "*.dmp")),
                   key=os.path.getmtime, reverse=True)
    if dumps:
        latest = dumps[0]
        print(f"[*] Crash causado por IOCTL {state['current']}")
        print(f"    Buffer size: {state['buf_size']}")
        print(f"    Minidump: {latest}")
        # Usar WinDBG o dumpchk.exe para analizar
        return state['current'], latest
    return None, None
