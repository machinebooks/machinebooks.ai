# Extraído de: LibroBugBounty/cap-22-caso-asus.md
# El pipe asuscert existe y acepta conexiones
ok = kernel32.WaitNamedPipeW(
    r"\\.\pipe\asuscert", 1000
)
# Resultado: ok=1 (pipe existe)
# Protocolo: enviar DWORD PID -> recibir 'OK!'
# Validacion: WinVerifyTrust sobre el binario del caller
