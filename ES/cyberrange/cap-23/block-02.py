# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: services/trafgen.py
async def _replay_pcap(pcap_file: str, iface: str):
    """Reproducir un PCAP publicando progreso en tiempo real"""
    cmd = ["tcpreplay", "--intf1", iface, pcap_file]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    async for line in proc.stdout:
        await event_bus.publish("traffic.logs", line.rstrip())
    await proc.wait()
