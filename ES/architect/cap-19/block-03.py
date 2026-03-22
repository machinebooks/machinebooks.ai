# Extraído de: LibroTecnico/cap-19-testing-ia.md
import pytest
from unittest.mock import patch, MagicMock
from anthropic.types import Message, ContentBlock, Usage


def make_mock_message(content: str) -> Message:
    """Construye un objeto Message de Anthropic simulado para tests."""
    mock_block = MagicMock(spec=ContentBlock)
    mock_block.text = content
    mock_block.type = "text"

    mock_usage = MagicMock(spec=Usage)
    mock_usage.input_tokens = 450
    mock_usage.output_tokens = 320

    mock_msg = MagicMock(spec=Message)
    mock_msg.content = [mock_block]
    mock_msg.usage = mock_usage
    mock_msg.model = "claude-sonnet-4-6"
    mock_msg.stop_reason = "end_turn"
    return mock_msg


class TestDocumentAnalyzerEndpoint:
    """
    Tests de integración para el analizador documental.
    Verifican flujo, schema y persistencia — NO la calidad del output.
    """

    MOCK_ANALYSIS_RESPONSE = """{
        "summary": "Documento de requisitos para servicio de migración cloud.",
        "recommendation": "GO",
        "confidence": 0.82,
        "key_requirements": ["Migración en 6 meses", "SLA 99.9%", "GDPR compliance"],
        "risk_factors": ["Plazo ajustado", "Integración con sistema legado"]
    }"""

    @patch("anthropic.Anthropic")
    def test_analysis_returns_correct_schema(self, mock_anthropic_class, client, auth_headers):
        """Verifica que el endpoint devuelve el schema JSON esperado."""
        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.return_value = make_mock_message(
            self.MOCK_ANALYSIS_RESPONSE
        )

        response = client.post(
            "/api/documents/analyze",
            json={"document_id": "doc-test-001"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()

        # Verificar schema, no contenido
        assert "recommendation" in data
        assert data["recommendation"] in ("GO", "NO-GO", "REVIEW")
        assert "confidence" in data
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0

