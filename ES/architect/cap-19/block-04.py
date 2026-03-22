# Extraído de: LibroTecnico/cap-19-testing-ia.md
    @patch("anthropic.Anthropic")
    def test_analysis_logs_usage_to_audit(self, mock_anthropic_class, client, auth_headers, db_session):
        """Verifica que la llamada queda registrada en LLMUsageLog."""
        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.return_value = make_mock_message(
            self.MOCK_ANALYSIS_RESPONSE
        )

        client.post(
            "/api/documents/analyze",
            json={"document_id": "doc-test-001"},
            headers=auth_headers,
        )

        # Verificar que se creó el registro de uso
        from models.llm_usage_log import LLMUsageLog
        log = db_session.query(LLMUsageLog).filter_by(
            service_type="document_analysis"
        ).first()

        assert log is not None
        assert log.input_tokens > 0
        assert log.output_tokens > 0
        assert log.model_used == "claude-sonnet-4-6"

    @patch("anthropic.Anthropic")
    def test_analysis_handles_rate_limit_error(self, mock_anthropic_class, client, auth_headers):
        """Verifica el comportamiento cuando la API devuelve rate limit."""
        from anthropic import RateLimitError

        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.side_effect = RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={}
        )

        response = client.post(
            "/api/documents/analyze",
            json={"document_id": "doc-test-001"},
            headers=auth_headers,
        )

        # El sistema debe devolver error manejado, no excepción
        assert response.status_code == 429
        data = response.get_json()
        assert "retry_after" in data
