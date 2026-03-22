# Extraído de: LibroTecnico/cap-18-brecha-testing.md
# tests/test_health_checks.py - añadido al bloque de tests de integración

class TestHealthCheckConfiguracion:
    """
    Tests que verifican la correcta configuración del entorno a través del
    health check. Deben ejecutarse en el pipeline de despliegue contra el
    entorno real, no contra la BD de testing en memoria.
    """

    @pytest.mark.integration
    def test_todas_las_bases_de_datos_responden(self, client, auth_headers_by_role):
        """Las tres bases de datos deben estar configuradas y disponibles."""
        response = client.get("/api/health/full", headers=auth_headers_by_role["admin"])
        datos = response.json
        servicios = {s["name"]: s for s in datos.get("services", [])}

        for db_name in ["database_operations", "database_platform", "database_analytics"]:
            assert db_name in servicios, f"BD '{db_name}' no configurada"
            assert servicios[db_name]["status"] == "healthy", \
                f"BD '{db_name}' reporta estado: {servicios[db_name]['status']}"

    @pytest.mark.integration
    def test_servicio_ia_accesible_desde_backend(self, client, auth_headers_by_role):
        """El servicio de IA debe ser accesible desde el backend."""
        response = client.get("/api/health/full", headers=auth_headers_by_role["admin"])
        datos = response.json
        servicios = {s["name"]: s for s in datos.get("services", [])}

        assert "ai_service" in servicios, "El servicio de IA no está configurado"
        # En staging puede estar degradado si los modelos no están disponibles
        # pero debe estar registrado como servicio
        assert servicios["ai_service"]["status"] in ["healthy", "degraded"]
