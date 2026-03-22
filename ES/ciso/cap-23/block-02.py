# Extraído de: LibroCISO/cap-23-testing-grc.md
class TestArt33Brechas:
    """Verificación del plazo de notificación Art. 33 RGPD."""

    @pytest.mark.regulatory
    async def test_brecha_plazo_72h_dentro(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Art. 33.1: notificación dentro de 72h → estado válido."""
        from datetime import datetime, timedelta

        ahora = datetime.utcnow()
        brecha = {
            "titulo": "Acceso no autorizado a base de datos",
            "fecha_deteccion": (ahora - timedelta(hours=48)).isoformat(),
            "fecha_notificacion_aepd": ahora.isoformat(),
            "categorias_datos_afectados": "Datos identificativos",
            "num_afectados_aprox": 150,
            "medidas_adoptadas": "Revocación de credenciales, parcheo",
        }
        resp = await client.post(
            "/api/v1/privacy/brechas", json=brecha, headers=auth_headers
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["plazo_72h_cumplido"] is True

    @pytest.mark.regulatory
    async def test_brecha_plazo_72h_excedido_alerta(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Art. 33.1: si han pasado más de 72h sin notificación,
        el sistema debe marcar la brecha como fuera de plazo
        y generar una alerta al DPO."""
        from datetime import datetime, timedelta

        ahora = datetime.utcnow()
        brecha = {
            "titulo": "Fuga de datos por email masivo",
            "fecha_deteccion": (ahora - timedelta(hours=80)).isoformat(),
            "fecha_notificacion_aepd": None,  # Aún no notificada
            "categorias_datos_afectados": "Datos de salud",
            "num_afectados_aprox": 2000,
            "medidas_adoptadas": "Investigación en curso",
        }
        resp = await client.post(
            "/api/v1/privacy/brechas", json=brecha, headers=auth_headers
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["plazo_72h_cumplido"] is False
        assert data["alerta_dpo_generada"] is True
