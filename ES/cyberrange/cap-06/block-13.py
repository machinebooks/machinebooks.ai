# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Métricas agregadas del cluster para capacidad de despliegue

if action == "cluster.status":
    nodes = client.nodes.get()
    totals = {
        "cpu_cores": 0, "mem_total": 0, "mem_used": 0,
        "cpu_used_sum": 0.0, "cpu_weight": 0
    }
    total_vms = running_vms = 0

    for node in nodes:
        maxcpu = node.get("maxcpu", 0)
        maxmem = node.get("maxmem", 0)
        cpu_pct = (node.get("cpu", 0) or 0.0) * 100.0

        totals["cpu_cores"] += maxcpu
        totals["mem_total"] += maxmem
        totals["mem_used"] += node.get("mem", 0)
        totals["cpu_used_sum"] += cpu_pct * maxcpu
        totals["cpu_weight"] += maxcpu

        # Contar VMs y contenedores por nodo
        qemu_vms = client.nodes(node["node"]).qemu.get()
        lxc_cts = client.nodes(node["node"]).lxc.get()
        total_vms += len(qemu_vms) + len(lxc_cts)
        running_vms += sum(
            1 for x in (qemu_vms + lxc_cts)
            if x.get("status") == "running"
        )

    return {
        "success": True,
        "result": {
            "resources": {
                "cpu": {
                    "total_cores": totals["cpu_cores"],
                    "used_percent": cpu_avg
                },
                "memory": {
                    "total_gb": totals["mem_total"] / (1024**3),
                    "used_gb": totals["mem_used"] / (1024**3),
                    "used_percent": mem_pct
                }
            },
            "vms": {
                "total": total_vms,
                "running": running_vms,
                "stopped": total_vms - running_vms
            }
        }
    }
