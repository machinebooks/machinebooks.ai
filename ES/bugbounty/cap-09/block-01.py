# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
# Pasada de bytes crudos para IOCTLs en tablas de constantes
for i in range(0, len(sec_data) - 3):
    val = struct.unpack("<I", sec_data[i:i+4])[0]
    if is_valid_ioctl(val, device_types):
        if val not in found:
            found[val] = [{"address": hex(sec_va + i),
                           "instruction": "raw_bytes"}]
