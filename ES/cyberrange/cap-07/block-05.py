# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/port_mirror.py — Captura de tráfico

class PortMirrorService:
    """Captura de paquetes en interfaces de red de workzones."""

    def __init__(self):
        self.active_captures: dict[str, dict] = {}
        self.capture_dir = "/tmp/cyberrange_captures"
        os.makedirs(self.capture_dir, exist_ok=True)

    def start_capture(self, interface: str, workzone_id: int,
                      filter_expr: str = "",
                      max_packets: int = 10000,
                      duration_seconds: int = 300) -> dict:
        """Iniciar captura de paquetes en una interfaz."""
        capture_id = (
            f"wz{workzone_id}_{interface}_"
            f"{int(datetime.utcnow().timestamp())}"
        )
        output_file = os.path.join(
            self.capture_dir, f"{capture_id}.pcap"
        )

        cmd = [
            "tcpdump", "-i", interface,
            "-w", output_file,
            "-c", str(max_packets),
        ]
        if filter_expr:
            # Sanitizar: solo permitir caracteres válidos en filtros BPF
            # para evitar inyección de comandos vía filter_expr
            import re
            if not re.match(r'^[a-zA-Z0-9\s\.\:\/\-\(\)&|!=<>]+$', filter_expr):
                raise ValueError(f"Filtro BPF no válido: {filter_expr}")
            cmd.extend(filter_expr.split())

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.active_captures[capture_id] = {
            "id": capture_id,
            "interface": interface,
            "workzone_id": workzone_id,
            "output_file": output_file,
            "process": proc,
            "pid": proc.pid,
            "status": "capturing",
            "max_packets": max_packets,
            "filter": filter_expr,
        }
        return self.active_captures[capture_id]

    def stop_capture(self, capture_id: str) -> dict:
        """Detener una captura activa y devolver metadatos."""
        cap = self.active_captures[capture_id]
        proc = cap.get("process")
        if proc and proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)
        cap["status"] = "completed"
        if os.path.exists(cap["output_file"]):
            cap["file_size"] = os.path.getsize(cap["output_file"])
        return cap
