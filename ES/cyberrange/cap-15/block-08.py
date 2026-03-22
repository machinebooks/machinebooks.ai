# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
TRAFFIC_LIB = os.getenv("TRAFFIC_LIB", "/opt/traffic-profiles")

async def _replay_pcap(pcap_file: str, iface: str):
    """Reproduce un PCAP en la interfaz de red del escenario."""
    cmd = ["tcpreplay", "--intf1", iface, pcap_file]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    async for raw in proc.stdout:
        await event_bus.publish("traffic.logs", raw.decode(errors="replace").rstrip())
    await proc.wait()

async def schedule_profile(profile: str, iface: str = "eth0"):
    """
    Ejecuta un perfil de tráfico:
    - .pcap → tcpreplay (reproduce captura real)
    - .py   → Scapy script (genera tráfico sintético)
    """
    path = os.path.join(TRAFFIC_LIB, profile)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    if profile.endswith(".pcap"):
        await _replay_pcap(path, iface)
    elif profile.endswith(".py"):
        proc = await asyncio.create_subprocess_exec(
            "python", path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        async for raw in proc.stdout:
            await event_bus.publish("traffic.logs", raw.decode(errors="replace").rstrip())
        await proc.wait()
    else:
        raise ValueError("Tipo de perfil de tráfico no soportado")
