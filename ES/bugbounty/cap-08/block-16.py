# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
def r2_cross_reference_analysis(driver_path, target_function):
    """Análisis de cross-references con r2pipe."""
    r2 = r2pipe.open(str(driver_path), flags=["-2"])
    r2.cmd("aaa")  # Análisis completo

    # Buscar imports que coincidan con la función target
    imports = r2.cmdj("iij") or []
    target_addr = None
    for imp in imports:
        if target_function in imp.get("name", ""):
            target_addr = imp.get("plt", 0)
            break

    if not target_addr:
        return {"error": f"{target_function} not found in imports"}

    # Obtener todas las funciones que llaman a target
    xrefs = r2.cmdj(f"axtj {target_addr}") or []
    callers = []
    for xref in xrefs:
        caller_addr = xref.get("fcn_addr", 0)
        if caller_addr:
            func_info = r2.cmdj(f"afij @ {caller_addr}")
            if func_info:
                callers.append({
                    "address": hex(caller_addr),
                    "name": func_info[0].get("name", "unknown"),
                    "size": func_info[0].get("size", 0),
                    "xref_addr": hex(xref.get("from", 0)),
                })

    r2.quit()
    return {
        "target": target_function,
        "target_addr": hex(target_addr),
        "callers": callers,
        "total_xrefs": len(callers),
    }
