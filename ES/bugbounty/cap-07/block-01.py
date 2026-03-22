# Extraído de: LibroBugBounty/cap-07-firma-codigo.md
# AnÃ¡lisis de la cadena de carga de CoworkVMService.exe
# (Modelo local â€” material pre-disclosure de Anthropic)

# El flujo de bypass identificado:
#
# 1. CoworkVMService.exe se inicia como SYSTEM
# 2. Carga DLLs del directorio de la aplicaciÃ³n
#    (directorio con permisos para el usuario)
# 3. Entre esas DLLs, puede cargarse una proxy DLL
# 4. La proxy DLL hookea WinVerifyTrust en ntdll/wintrust.dll
# 5. A partir de este punto, cualquier llamada a WinVerifyTrust
#    devuelve ERROR_SUCCESS
# 6. El servicio verifica la "firma" de un binario malicioso
# 7. WinVerifyTrust (hookeado) devuelve "vÃ¡lido"
# 8. El servicio ejecuta el binario malicioso como SYSTEM

# Impacto: escalada de privilegios de usuario a SYSTEM
# via bypass de verificaciÃ³n de firma en un servicio
# que se ejecuta con mÃ¡ximos privilegios
