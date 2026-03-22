# Extraído de: LibroBugBounty/cap-10-memory-corruption.md
anim = win32com.client.Dispatch(
    "{756E6C18-79CC-3842-9E47-7C80011D303A}"
)
anim.init(10, 10)

layer1 = anim.CreateLayer()
layer2 = anim.CreateLayer()
anim.AddLayer(layer1)
anim.AddLayer(layer2)

# Clear elimina ambos layers internamente
anim.ClearLayers()

# Pero layer1 y layer2 siguen siendo referencias válidas
# Cualquier operación sobre ellos es una stale reference
anim.RemoveLayer(layer1)  # Stale reference — memoria ya liberada

# Peor: reusar layer1 después de crear nuevos layers
layer3 = anim.CreateLayer()
anim.AddLayer(layer3)
# layer1 puede ahora apuntar al mismo bloque de memoria que layer3
# Operaciones sobre layer1 corrompen layer3
