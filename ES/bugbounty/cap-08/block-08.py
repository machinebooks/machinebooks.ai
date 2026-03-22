# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
def heuristic_dispatch_search(r2):
    """Búsqueda heurística cuando el patrón estándar no funciona."""
    # Buscar imports de IoCompleteRequest
    imports = r2.cmdj("iij") or []
    io_complete = None
    for imp in imports:
        if "IoCompleteRequest" in imp.get("name", ""):
            io_complete = imp.get("plt", 0)
            break

    if not io_complete:
        return {}

    # Encontrar funciones que la llaman
    xrefs = r2.cmdj(f"axtj {io_complete}") or []
    candidates = set()
    for xref in xrefs:
        addr = xref.get("fcn_addr", 0)
        if addr:
            candidates.add(addr)

    # Filtrar funciones triviales (< 100 bytes)
    handlers = {}
    for addr in sorted(candidates):
        func_info = r2.cmdj(f"afij @ {addr}")
        if func_info and func_info[0].get("size", 0) > 100:
            handlers[addr] = {
                "irp_type": "CANDIDATE",
                "handler_ref": func_info[0].get("name", hex(addr)),
                "address": hex(addr),
            }

    return handlers
