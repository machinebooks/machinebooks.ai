# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
from boofuzz import Session, Target, SocketConnection
from boofuzz import s_initialize, s_dword, s_bytes, s_string

# Fuzzing del protocolo del pipe de AsusCertService
session = Session(
    target=Target(
        connection=SocketConnection(
            "127.0.0.1", 0,  # Named pipe via SMB local
            proto="tcp"
        )
    ),
    crash_threshold_element=5,
    crash_threshold_request=10,
)

# Modelamos el protocolo observado del pipe
s_initialize("register_pid")
s_dword(0x01, name="command", fuzzable=True)
s_dword(0x00, name="pid", fuzzable=True)
s_bytes(b"\x00" * 256, name="cert_data", max_len=4096)
