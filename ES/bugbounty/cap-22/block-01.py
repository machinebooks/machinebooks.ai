# Extraído de: LibroBugBounty/cap-22-caso-asus.md
anim = win32com.client.Dispatch(CLSID_AURA)
anim.init(10, 10)
layer = anim.CreateLayer()

# Todos estos indices son aceptados sin error:
anim.InsertLayerAt(-1, layer)             # Indice negativo
anim.InsertLayerAt(999, layer)            # Muy superior al tamano
anim.InsertLayerAt(2147483647, layer)     # INT_MAX
anim.InsertLayerAt(-2147483648, layer)    # INT_MIN
