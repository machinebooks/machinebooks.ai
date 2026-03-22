# Extraído de: LibroBugBounty/cap-07-firma-codigo.md
# AnÃ¡lisis del flujo de actualizaciÃ³n de Squirrel en Discord
# (Claude Code â€” cÃ³digo de Squirrel es pÃºblico)

# Squirrel ejecuta Update.exe con argumentos especiales:
# --squirrel-install       â†’ primera instalaciÃ³n
# --squirrel-updated       â†’ despuÃ©s de cada actualizaciÃ³n
# --squirrel-obsolete      â†’ al eliminar versiÃ³n antigua
# --squirrel-uninstall     â†’ al desinstalar

# El ejecutable principal de la app recibe estos argumentos
# y debe procesarlos. Si el main.js de Electron procesa
# --squirrel-updated, puede ejecutar cÃ³digo en cada update.

# Discord main.js (extracto del anÃ¡lisis del ASAR):
# if (process.argv.includes('--squirrel-updated')) {
#     // CÃ³digo que se ejecuta despuÃ©s de cada actualizaciÃ³n
#     // Si este cÃ³digo estÃ¡ en un ASAR tampered, se ejecuta
#     // con cada actualizaciÃ³n, creando persistencia
# }
