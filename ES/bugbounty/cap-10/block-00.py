# Extraído de: LibroBugBounty/cap-10-memory-corruption.md
import win32com.client

# Instanciar sin privilegios de administrador
anim = win32com.client.Dispatch(
    "{756E6C18-79CC-3842-9E47-7C80011D303A}"
)
