# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
def fuzz_with_checkpoint(handle, ioctl_codes, checkpoint_file="state.json"):
    """Fuzzing con estado persistente — se recupera tras BSOD."""
    import json

    # Cargar estado previo (después de reinicio post-BSOD)
    try:
        with open(checkpoint_file) as f:
            state = json.load(f)
        start_idx = state.get("last_completed", 0) + 1
    except FileNotFoundError:
        start_idx = 0

    for idx, (code, buf) in enumerate(generate_test_cases(ioctl_codes)):
        if idx < start_idx:
            continue

        # Guardar checkpoint ANTES de enviar
        with open(checkpoint_file, 'w') as f:
            json.dump({"last_completed": idx - 1,
                        "current": hex(code),
                        "buf_size": len(buf)}, f)

        ok, err, out, ret = send_ioctl(handle, code, buf, len(buf))

        # Si llegamos aquí, no hubo BSOD
        with open(checkpoint_file, 'w') as f:
            json.dump({"last_completed": idx, "current": None}, f)
