# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/trafgen.py — Generación de tráfico

TRAFFIC_LIB = os.getenv(
    "TRAFFIC_LIB", "/opt/traffic-profiles"
)

async def _replay_pcap(pcap_file: str, iface: str):
    """Reproducir un fichero PCAP en una interfaz de red."""
    cmd = ["tcpreplay", "--intf1", iface, pcap_file]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    async for line in proc.stdout:
        # Publicar progreso en tiempo real vía WebSocket
        await event_bus.publish(
            "traffic.logs", line.decode().rstrip()
        )
    await proc.wait()

async def schedule_profile(profile: str,
                           iface: str = "eth0"):
    """Ejecutar un perfil de tráfico.
    - .pcap → tcpreplay
    - .py   → script Scapy
    """
    path = os.path.join(TRAFFIC_LIB, profile)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    if profile.endswith(".pcap"):
        await _replay_pcap(path, iface)
    elif profile.endswith(".py"):
        cmd = ["python", path]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        async for line in proc.stdout:
            await event_bus.publish(
                "traffic.logs", line.decode().rstrip()
            )
        await proc.wait()
    else:
        raise ValueError(
            "Tipo de perfil de tráfico no soportado"
        )
