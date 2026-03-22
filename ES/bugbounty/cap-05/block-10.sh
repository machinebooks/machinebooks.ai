# Extraído de: LibroBugBounty/cap-05-asar-tampering.md
# Instalar la herramienta oficial
npm install -g @electron/asar

# Extraer todo el contenido del ASAR a un directorio
asar extract app.asar app_extracted/

# Listar ficheros dentro del ASAR
asar list app.asar

# Crear un nuevo ASAR desde un directorio
asar pack app_extracted/ app_new.asar
