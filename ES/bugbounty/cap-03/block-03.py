# Extraído de: LibroBugBounty/cap-03-etica-legalidad.md
# Ejemplo: Claude calcula CVSS para DLL hijacking en Discord
# El investigador valida cada mÃ©trica

cvss_analysis = """
Attack Vector (AV): Local (L) â€” requiere acceso al filesystem local
Attack Complexity (AC): Low (L) â€” no requiere condiciones especiales
Privileges Required (PR): Low (L) â€” cualquier usuario puede escribir
                                      en %LOCALAPPDATA%
User Interaction (UI): Required (R) â€” el usuario debe iniciar Discord
Scope (S): Unchanged (U) â€” el impacto se limita al contexto del usuario
Confidentiality (C): High (H) â€” acceso completo a tokens de sesiÃ³n
Integrity (I): High (H) â€” ejecuciÃ³n de cÃ³digo arbitrario
Availability (A): Low (L) â€” la app sigue funcionando

Score: 7.3 (High)
Vector: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L
"""

# NOTA: Claude inicialmente calculÃ³ PR:N (None),
# argumentando que "cualquier usuario" equivale a "sin privilegios".
# El investigador corrigiÃ³ a PR:L porque el atacante necesita
# al menos una sesiÃ³n de usuario en el sistema.
# Esa correcciÃ³n bajÃ³ el score de 7.8 a 7.3.
