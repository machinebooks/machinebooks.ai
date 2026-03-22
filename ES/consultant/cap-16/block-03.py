# Extraído de: LibroConsultor/cap-16-roadmaps-ia.md
from collections import defaultdict, deque

def secuenciar_iniciativas(iniciativas: list[Iniciativa]) -> list[Iniciativa]:
    """Ordena iniciativas respetando dependencias y maximizando prioridad."""
    # Construir grafo de dependencias
    nombre_a_ini = {i.nombre: i for i in iniciativas}
    grafo = defaultdict(list)
    grado_entrada = defaultdict(int)

    for ini in iniciativas:
        if ini.nombre not in grado_entrada:
            grado_entrada[ini.nombre] = 0
        for dep in ini.dependencias:
            if dep in nombre_a_ini:
                grafo[dep].append(ini.nombre)
                grado_entrada[ini.nombre] += 1

    # Ordenación topológica con prioridad (Kahn + heap)
    import heapq
    # Nodos sin dependencias pendientes, ordenados por prioridad descendente
    cola = []
    for nombre, grado in grado_entrada.items():
        if grado == 0:
            ini = nombre_a_ini[nombre]
            heapq.heappush(cola, (-ini.prioridad, nombre))

    resultado = []
    while cola:
        _, nombre = heapq.heappop(cola)
        resultado.append(nombre_a_ini[nombre])
        for sucesor in grafo[nombre]:
            grado_entrada[sucesor] -= 1
            if grado_entrada[sucesor] == 0:
                ini_suc = nombre_a_ini[sucesor]
                heapq.heappush(cola, (-ini_suc.prioridad, sucesor))

    # Detectar ciclos
    if len(resultado) != len(iniciativas):
        ciclo = [i.nombre for i in iniciativas
                 if i.nombre not in {r.nombre for r in resultado}]
        raise ValueError(f"Dependencias circulares detectadas: {ciclo}")

    return resultado
