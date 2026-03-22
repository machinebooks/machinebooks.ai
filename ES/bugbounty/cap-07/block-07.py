# Extraído de: LibroBugBounty/cap-07-firma-codigo.md
# Impacto de la evasiÃ³n de EDR: escenario documentado en el report
#
# Sin bypass de firma (detectable):
# malware.exe â†’ abre conexiÃ³n a C2 â†’ EDR ALERTA
#
# Con bypass via ASAR tampering (no detectable):
# Discord.exe (firmado) â†’ payload en main.js â†’ abre conexiÃ³n
# â†’ EDR: "Discord conectÃ¡ndose a internet, comportamiento normal"
#
# Con bypass via DLL sideloading (difÃ­cilmente detectable):
# Steam.exe (firmado) â†’ VERSION.dll (proxy) â†’ payload en DllMain
# â†’ EDR: "Steam cargando DLL del sistema, comportamiento normal"
#
# El mismo payload, pero el envoltorio de confianza cambia todo.
