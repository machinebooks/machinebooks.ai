# Extraído de: LibroTecnico/cap-18-brecha-testing.md
# tests/mocks/llm_mock.py
from unittest.mock import MagicMock, patch
from contextlib import contextmanager

RESPUESTA_ANALISIS_DOCUMENTO_OK = {
    "summary": "Documento de requisitos técnicos para implementación de sistema CRM.",
    "key_requirements": ["Alta disponibilidad", "Integración API REST", "GDPR compliance"],
    "go_no_go": "GO",
    "confidence": 0.87,
    "flags": []
}

RESPUESTA_LLM_MALFORMADA = "Este texto no es JSON válido {{{malformado"

RESPUESTA_LLM_VACIA = ""

@contextmanager
def mock_llm_respuesta_correcta():
    """Mock para tests que verifican el flujo feliz del análisis con IA."""
    with patch("app.services.ai.llm_factory.LLMFactory.create_completion") as mock:
        mock.return_value = MagicMock(
            content=str(RESPUESTA_ANALISIS_DOCUMENTO_OK),
            usage=MagicMock(input_tokens=450, output_tokens=120),
            model="claude-sonnet-4-6"
        )
        yield mock

@contextmanager
def mock_llm_respuesta_malformada():
    """Mock para tests que verifican el manejo de respuestas inválidas del LLM."""
    with patch("app.services.ai.llm_factory.LLMFactory.create_completion") as mock:
        mock.return_value = MagicMock(
            content=RESPUESTA_LLM_MALFORMADA,
            usage=MagicMock(input_tokens=450, output_tokens=5),
            model="claude-sonnet-4-6"
        )
        yield mock

@contextmanager
def mock_llm_timeout():
    """Mock para tests que verifican el comportamiento ante timeout del LLM."""
    with patch("app.services.ai.llm_factory.LLMFactory.create_completion") as mock:
        mock.side_effect = TimeoutError("LLM request timeout after 30s")
        yield mock
