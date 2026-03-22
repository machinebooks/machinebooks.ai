# Extraído de: LibroBugBounty/cap-17-poc-impacto.md
import pefile

pe = pefile.PE("C:/Windows/System32/version.dll")
for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    name = exp.name.decode() if exp.name else f"ordinal_{exp.ordinal}"
    print(f"  {name} (ordinal {exp.ordinal})")
pe.close()
# Output: 17 funciones exportadas
