# Extraído de: LibroBugBounty/cap-10-memory-corruption.md
import win32com.client
import random
import traceback

def fuzz_com_class(clsid, methods_to_fuzz, iterations=1000):
    """Fuzzer básico de interfaz COM."""
    obj = win32com.client.Dispatch(clsid)

    # Inicializar si tiene método init
    try:
        obj.init(10, 10)
    except Exception:
        pass

    crashes = []
    for i in range(iterations):
        method_name = random.choice(methods_to_fuzz)
        try:
            method = getattr(obj, method_name)
            # Generar argumentos aleatorios
            args = generate_random_args(method_name)
            method(*args)
        except Exception as e:
            error_type = type(e).__name__
            if "memory" in str(e).lower() or "access" in str(e).lower():
                crashes.append({
                    "iteration": i,
                    "method": method_name,
                    "error": str(e),
                    "type": error_type,
                })

    return crashes

def generate_random_args(method_name):
    """Genera argumentos de fuzzing según el método."""
    if method_name == "InsertLayerAt":
        # Fuzzing de índice: valores negativos, muy grandes, cero
        return [random.choice([-1, 0, 999, 2**31-1, 2**32-1]), None]
    elif method_name in ("AddLayer", "RemoveLayer"):
        return [None]  # Pasar None como layer — null dereference?
    elif method_name == "init":
        return [random.randint(-100, 10000), random.randint(-100, 10000)]
    return []
