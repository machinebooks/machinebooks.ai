# Extraído de: LibroTecnico/cap-20-docker.md
        # Ejecutar todas las verificaciones en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                # Los tres MySQL
                executor.submit(check_mysql, 'mysql_ops', self.dbs['ops']),
                executor.submit(check_mysql, 'mysql_core', self.dbs['core']),
                executor.submit(check_mysql, 'mysql_analytics', self.dbs['analytics']),
                # Redis
                executor.submit(lambda: ('redis', self._check_redis())),
                # Servicios HTTP externos al backend
                executor.submit(check_http_service, 'ai_service',
                                'http://ai_service:8001/health'),
                executor.submit(check_http_service, 'meilisearch',
                                'http://meilisearch:7700/health'),
                executor.submit(check_http_service, 'qdrant',
                                'http://qdrant:6333/healthz'),
                # Celery (workers + beat)
                executor.submit(check_celery_workers, 'celery_workers'),
                # Los tres frontales Nginx
                executor.submit(check_http_service, 'frontend_ops',
                                'http://nginx_ops:80/health'),
                executor.submit(check_http_service, 'frontend_analytics',
                                'http://nginx_analytics:80/health'),
                executor.submit(check_http_service, 'frontend_admin',
                                'http://nginx_admin:80/health'),
            ]
            for future in concurrent.futures.as_completed(futures):
                name, result = future.result()
                checks[name] = result

        # Calcular estado global
        statuses = [c['status'] for c in checks.values()]
        if all(s == 'healthy' for s in statuses):
            overall = "healthy"
        elif any(s == 'unhealthy' for s in statuses):
            overall = "unhealthy"
        else:
            overall = "degraded"

        return {
            "status": overall,
            "checks": checks,
            "mode": "full",
            "timestamp": time.time()
        }

    def _check_redis(self) -> dict:
        start = time.monotonic()
        try:
            info = self.redis.info()
            return {
                "status": "healthy",
                "latency_ms": round((time.monotonic() - start) * 1000, 2),
                "used_memory_mb": round(info['used_memory'] / 1024 / 1024, 1),
                "connected_clients": info['connected_clients']
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
