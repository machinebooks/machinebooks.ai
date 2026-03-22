# Extraído de: LibroTecnico/cap-18-brecha-testing.md
# tests/test_analisis_documentos.py

class TestAnalisisDocumentos:

    def test_analisis_documento_correcto_devuelve_resumen(
        self, client, auth_headers_by_role
    ):
        """Cuando el LLM responde correctamente, el endpoint devuelve el análisis."""
        with mock_llm_respuesta_correcta():
            response = client.post(
                "/api/v1/documents/1/analyze",
                headers=auth_headers_by_role["analyst"]
            )
        assert response.status_code == 200
        datos = response.json
        assert "summary" in datos
        assert "go_no_go" in datos
        assert datos["go_no_go"] in ["GO", "NO_GO", "REVIEW"]

    def test_respuesta_malformada_llm_no_provoca_error_500(
        self, client, auth_headers_by_role
    ):
        """
        Si el LLM devuelve texto que no es JSON válido, el endpoint debe
        manejar el error grácilmente y devolver 422, no 500.
        Un 500 aquí indicaría que el parsing de la respuesta no tiene manejo de errores.
        """
        with mock_llm_respuesta_malformada():
            response = client.post(
                "/api/v1/documents/1/analyze",
                headers=auth_headers_by_role["analyst"]
            )
        assert response.status_code != 500, \
            "El sistema no debe caer ante respuestas malformadas del LLM"
        assert response.status_code in [422, 503]

    def test_timeout_llm_devuelve_503_con_retry_after(
        self, client, auth_headers_by_role
    ):
        """Un timeout del LLM debe devolver 503 con cabecera Retry-After."""
        with mock_llm_timeout():
            response = client.post(
                "/api/v1/documents/1/analyze",
                headers=auth_headers_by_role["analyst"]
            )
        assert response.status_code == 503
        assert "Retry-After" in response.headers
