# Extraído de: LibroCISO/cap-23-testing-grc.md
# tests/qa/qa_privacy.py (sección PII)

class TestPIIDetector:
    """Verificación del detector de datos personales."""

    # Positivos: datos reales que DEBEN detectarse
    POSITIVOS = [
        ("12345678Z", "dni", "DNI español con letra"),
        ("ES12 1234 5678 90 1234567890", "iban", "IBAN español"),
        ("4111 1111 1111 1111", "tarjeta", "Visa de test"),
        ("nombre.apellido@empresa.com", "email", "Email corporativo"),
    ]

    # Negativos: textos que NO deben generar detección
    NEGATIVOS = [
        ("El artículo 12345678 del reglamento", "No es DNI"),
        ("Código de referencia: ES12-ABCD", "No es IBAN"),
        ("Llamar al 911 en caso de emergencia", "No es teléfono personal"),
    ]

    @pytest.mark.parametrize("texto,tipo,desc", POSITIVOS)
    async def test_pii_deteccion_positiva(
        self, client, auth_headers, texto, tipo, desc
    ):
        """El detector debe identificar PII real en texto libre."""
        resp = await client.post(
            "/api/v1/ai/pii/detect",
            json={"text": f"El usuario con documento {texto} solicitó acceso"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        detecciones = resp.json()["detections"]
        tipos = [d["type"] for d in detecciones]
        assert tipo in tipos, f"PII no detectado: {desc} ({texto})"

    @pytest.mark.parametrize("texto,desc", NEGATIVOS)
    async def test_pii_falsos_positivos(self, client, auth_headers, texto, desc):
        """El detector NO debe generar falsas alarmas con textos
        que parecen PII pero no lo son. Cada falso positivo es una
        alerta que el usuario ignora — y cuando ignore la correcta,
        tendremos un problema real."""
        resp = await client.post(
            "/api/v1/ai/pii/detect",
            json={"text": texto},
            headers=auth_headers,
        )
        data = resp.json()
        assert len(data["detections"]) == 0, (
            f"Falso positivo: '{texto}' fue detectado como PII ({desc})"
        )
