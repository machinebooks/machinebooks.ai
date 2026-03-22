# Extraído de: LibroTecnico/cap-20-docker.md
    def full_check(self) -> dict:
        """
        Verificación completa de los 11 servicios de la plataforma.
        Diseñado para uso manual (operaciones), no como readiness probe.
        Ejecuta verificaciones en paralelo para reducir latencia total.
        """
        import concurrent.futures

        checks = {}

        def check_mysql(name: str, session) -> tuple:
            start = time.monotonic()
            try:
                session.execute(text("SELECT 1"))
                return name, {"status": "healthy",
                              "latency_ms": round((time.monotonic() - start) * 1000, 2)}
            except Exception as e:
                return name, {"status": "unhealthy", "error": str(e)}

        def check_http_service(name: str, url: str, timeout: int = 5) -> tuple:
            start = time.monotonic()
            try:
                resp = requests.get(url, timeout=timeout)
                resp.raise_for_status()
                return name, {
                    "status": "healthy",
                    "latency_ms": round((time.monotonic() - start) * 1000, 2)
                }
            except Exception as e:
                return name, {"status": "unhealthy", "error": str(e)}

        def check_celery_workers(name: str) -> tuple:
            """
            Verifica que los workers de Celery están respondiendo mediante ping.
            Un worker que no responde al ping está muerto o bloqueado.
            """
            start = time.monotonic()
            try:
                control = Control(self.celery)
                # ping con timeout de 2s: si no responde, está inactivo
                response = control.ping(timeout=2.0)
                active_workers = len(response) if response else 0
                status = "healthy" if active_workers >= 3 else "degraded"
                return name, {
                    "status": status,
                    "active_workers": active_workers,
                    "latency_ms": round((time.monotonic() - start) * 1000, 2)
                }
            except Exception as e:
                return name, {"status": "unhealthy", "error": str(e)}

