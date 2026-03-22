# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: métricas agregadas del cluster
# Patrón: backend/services/proxmox_sdk_service.py (acción "cluster.status")

if action == "cluster.status":
    nodes = client.nodes.get()
    totals = {
        "cpu_cores": 0, "mem_total": 0, "mem_used": 0,
        "cpu_weighted_sum": 0.0, "cpu_weight": 0
    }
    total_vms = running_vms = stopped_vms = online_nodes = 0

    for node in nodes:
        node_name = node["node"]
        if node.get("status") == "online":
            online_nodes += 1

        maxcpu = node.get("maxcpu", 0)
        maxmem = node.get("maxmem", 0)
        cpu_pct = (node.get("cpu", 0) or 0.0) * 100.0
        mem_used = node.get("mem", 0)

        totals["cpu_cores"] += maxcpu
        totals["mem_total"] += maxmem
        totals["mem_used"] += mem_used
        # Media ponderada por número de cores
        totals["cpu_weighted_sum"] += cpu_pct * maxcpu
        totals["cpu_weight"] += maxcpu

        # Contar VMs por nodo (QEMU + LXC)
        vms = client.nodes(node_name).qemu.get()
        cts = client.nodes(node_name).lxc.get()
        all_items = vms + cts
        total_vms += len(all_items)
        running_vms += sum(1 for x in all_items if x["status"] == "running")
        stopped_vms += sum(1 for x in all_items if x["status"] == "stopped")

    return {
        "success": True,
        "result": {
            "resources": {
                "cpu": {
                    "total_cores": totals["cpu_cores"],
                    "used_percent": round(
                        totals["cpu_weighted_sum"] / totals["cpu_weight"], 2
                    ) if totals["cpu_weight"] else 0.0
                },
                "memory": {
                    "total_gb": round(totals["mem_total"] / 1073741824, 2),
                    "used_gb": round(totals["mem_used"] / 1073741824, 2)
                },
                "nodes": {
                    "total": len(nodes),
                    "online": online_nodes
                }
            },
            "vms": {
                "total": total_vms,
                "running": running_vms,
                "stopped": stopped_vms
            }
        }
    }
