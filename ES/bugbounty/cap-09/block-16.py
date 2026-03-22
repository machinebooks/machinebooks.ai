# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
import json
import datetime

class FuzzSession:
    """Documenta una sesión de fuzzing para el reporte."""

    def __init__(self, target, device_path):
        self.target = target
        self.device_path = device_path
        self.start_time = datetime.datetime.now()
        self.results = []
        self.crashes = []

    def log_ioctl(self, code, buf_size, ok, err, ret_bytes, notes=""):
        self.results.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "ioctl": hex(code),
            "buf_size": buf_size,
            "success": ok,
            "error": err,
            "ret_bytes": ret_bytes,
            "notes": notes,
        })

    def log_crash(self, ioctl_code, buf_size, crash_type):
        self.crashes.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "ioctl": hex(ioctl_code),
            "buf_size": buf_size,
            "crash_type": crash_type,
        })

    def save(self, output_path):
        session = {
            "target": self.target,
            "device": self.device_path,
            "start": self.start_time.isoformat(),
            "end": datetime.datetime.now().isoformat(),
            "total_ioctls_tested": len(self.results),
            "total_crashes": len(self.crashes),
            "results": self.results,
            "crashes": self.crashes,
        }
        with open(output_path, 'w') as f:
            json.dump(session, f, indent=2)
