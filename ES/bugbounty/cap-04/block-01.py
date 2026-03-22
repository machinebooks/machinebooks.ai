# Extraído de: LibroBugBounty/cap-04-electron-superficie.md
# Ejecución del audit contra Discord
result = full_audit(
    r"C:\Users\researcher\AppData\Local\Discord\app-1.0.9045\Discord.exe"
)

# Resultado (simplificado):
# {
#   "application": "Discord.exe",
#   "fuses": [
#     {"name": "RunAsNode", "enabled": true, ...},
#     {"name": "EnableCookieEncryption", "enabled": false, ...},
#     {"name": "EnableNodeOptionsEnvironmentVariable", "enabled": true, ...},
#     {"name": "OnlyLoadAppFromAsar", "enabled": false, ...},
#     {"name": "EnableEmbeddedAsarIntegrityValidation", "enabled": false, ...}
#   ],
#   "permissions": {
#     "writable_by_user": true,
#     "install_location": "C:\\Users\\...\\Discord\\app-1.0.9045",
#     "in_program_files": false
#   },
#   "asar": {
#     "asar_exists": true,
#     "asar_size": 14523648,
#     "app_dir_exists": false,
#     "app_dir_coexists": false
#   },
#   "critical_issues": [
#     "RunAsNode habilitado",
#     "Cifrado de cookies deshabilitado",
#     "ASAR integrity no forzada",
#     "Directorio escribible sin admin"
#   ],
#   "risk_level": "CRITICAL"
# }
