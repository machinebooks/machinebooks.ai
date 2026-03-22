# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
import pefile
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

cs = Cs(CS_ARCH_X86, CS_MODE_64)
cs.detail = True

METHOD_NAMES = {0: "BUFFERED", 1: "IN_DIRECT", 2: "OUT_DIRECT", 3: "NEITHER"}
ACCESS_NAMES = {0: "ANY", 1: "READ", 2: "WRITE", 3: "READ|WRITE"}

def decode_ioctl(code):
    """Descompone un CTL_CODE en sus campos."""
    device_type = (code >> 16) & 0xFFFF
    access      = (code >> 14) & 0x3
    function    = (code >>  2) & 0xFFF
    method      = code & 0x3
    return device_type, function, method, access

def scan_for_ioctls(filepath, device_types={0x22, 0x23, 0x24, 0x25}):
    """Escanea secciones ejecutables buscando constantes IOCTL."""
    pe = pefile.PE(str(filepath))
    data = filepath.read_bytes()
    image_base = pe.OPTIONAL_HEADER.ImageBase
    found = {}

    for section in pe.sections:
        if not (section.Characteristics & 0x20000000):  # Solo ejecutables
            continue
        sec_data = data[section.PointerToRawData:
                        section.PointerToRawData + section.SizeOfRawData]
        sec_va = image_base + section.VirtualAddress

        # Desensamblamos y buscamos inmediatos en comparaciones
        for insn in cs.disasm(sec_data, sec_va):
            if insn.mnemonic in ('cmp', 'sub', 'mov', 'test'):
                for part in insn.op_str.replace(',', ' ').split():
                    if part.startswith('0x'):
                        try:
                            val = int(part, 16) & 0xFFFFFFFF
                            dt, func, method, access = decode_ioctl(val)
                            if dt in device_types and func <= 0xFFF:
                                if val not in found:
                                    found[val] = []
                                found[val].append({
                                    "addr": hex(insn.address),
                                    "insn": f"{insn.mnemonic} {insn.op_str}",
                                })
                        except ValueError:
                            pass
    return found
