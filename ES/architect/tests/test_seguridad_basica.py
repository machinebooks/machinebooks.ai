# Extraído de: LibroTecnico/cap-18-brecha-testing.md
# tests/test_seguridad_basica.py

class TestAutenticacion:
    """Tests básicos de robustez del sistema de autenticación."""

    def test_login_credenciales_incorrectas_devuelve_401(self, client):
        """El sistema no debe dar pistas sobre qué campo es incorrecto."""
        response = client.post("/api/auth/login", json={
            "email": "usuario@ejemplo.com",
            "password": "contraseña_incorrecta"
        })
        assert response.status_code == 401
        # El mensaje no debe indicar si el email o la contraseña son incorrectos
        mensaje = response.json.get("message", "")
        assert "email" not in mensaje.lower()
        assert "usuario" not in mensaje.lower()
        assert "no encontrado" not in mensaje.lower()

    def test_token_expirado_devuelve_401(self, client, token_expirado):
        """Un JWT expirado debe ser rechazado incluso con firma válida."""
        response = client.get(
            "/api/v1/clients",
            headers={"Authorization": f"Bearer {token_expirado}"}
        )
        assert response.status_code == 401

    def test_token_manipulado_devuelve_401(self, client, token_valido):
        """Un token con payload modificado debe ser rechazado (firma inválida)."""
        partes = token_valido.split(".")
        payload_modificado = partes[1] + "XYZ"  # Corrompe el payload
        token_corrupto = f"{partes[0]}.{payload_modificado}.{partes[2]}"
        response = client.get(
            "/api/v1/clients",
            headers={"Authorization": f"Bearer {token_corrupto}"}
        )
        assert response.status_code == 401

    def test_rate_limiting_login_bloquea_intentos_excesivos(self, client):
        """Más de 5 intentos fallidos consecutivos deben resultar en 429."""
        # El umbral de rate limiting (5 intentos/minuto) se configura en el backend
        for _ in range(5):
            client.post("/api/auth/login", json={
                "email": "test@ejemplo.com",
                "password": "incorrecta"
            })
        response = client.post("/api/auth/login", json={
            "email": "test@ejemplo.com",
            "password": "incorrecta"
        })
        assert response.status_code == 429


class TestInyeccionSQL:
    """
    Tests básicos de resistencia a inyección SQL.
    No sustituyen un análisis de seguridad profesional,
    pero detectan las vulnerabilidades más obvias.
    """

    PAYLOADS_INYECCION = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1 UNION SELECT * FROM users--",
        "admin'--",
        "' OR 1=1--",
    ]

    @pytest.mark.parametrize("payload", PAYLOADS_INYECCION)
    def test_parametro_busqueda_resiste_inyeccion_sql(self, client, auth_headers_by_role):
        """El parámetro de búsqueda no debe ser vulnerable a inyección SQL básica."""
        response = client.get(
            f"/api/v1/clients?search={payload}",
            headers=auth_headers_by_role["analyst"]
        )
        # El endpoint debe responder 200 (búsqueda vacía) o 400 (validación)
        # Nunca debe resultar en error 500 (señal de que el payload llegó a la BD)
        assert response.status_code != 500, \
            f"Posible vulnerabilidad de inyección SQL con payload: {payload}"

    @pytest.mark.parametrize("payload", PAYLOADS_INYECCION)
    def test_campo_email_login_resiste_inyeccion(self, client):
        """El campo email del login no debe ser vulnerable a inyección SQL."""
        response = client.post("/api/auth/login", json={
            "email": payload,
            "password": "cualquier_cosa"
        })
        assert response.status_code != 500


class TestExposicionDatos:
    """Verifica que los endpoints no filtran campos sensibles en las respuestas."""

    def test_respuesta_usuario_no_contiene_hash_password(self, client, auth_headers_by_role):
        """El perfil de usuario nunca debe incluir el hash de contraseña."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_by_role["analyst"])
        assert response.status_code == 200
        datos = response.json
        assert "password" not in datos
        assert "password_hash" not in datos
        assert "hashed_password" not in datos

    def test_respuesta_cliente_no_expone_campos_internos(self, client, auth_headers_by_role):
        """Los datos de cliente no deben incluir campos de auditoría interna."""
        response = client.get("/api/v1/clients/1", headers=auth_headers_by_role["analyst"])
        if response.status_code == 200:
            datos = response.json
            campos_internos = ["_sa_instance_state", "deleted_at", "internal_notes"]
            for campo in campos_internos:
                assert campo not in datos, \
                    f"El campo interno '{campo}' no debería exponerse en la API"
