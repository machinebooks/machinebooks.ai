# Extraído de: LibroTecnico/cap-19-testing-ia.md
import pytest
import anthropic
from quality_scorer import LLMQualityScorer, QUALITY_PROFILES

# Marcador para indicar que estos tests requieren API key real
pytestmark = pytest.mark.real_api


class TestDocumentAnalysisQuality:
    """
    Tests de evaluación de calidad con modelo real.
    Se ejecutan en pipeline de evaluación periódica, no en CI estándar.
    """

    scorer = LLMQualityScorer()
    client = anthropic.Anthropic()

    # Documento de prueba: requisitos reales anonimizados
    TEST_DOCUMENT = """
    REQUISITOS DEL PROYECTO — Plataforma de Gestión de Incidencias

    1. El sistema debe procesar un máximo de 500 incidencias simultáneas.
    2. Tiempo de respuesta < 2 segundos para consultas de estado.
    3. Integración con sistema de tickets existente vía API REST.
    4. Retención de datos conforme a GDPR: máximo 24 meses.
    5. Disponibilidad: SLA 99.5% mensual.
    6. Autenticación: SSO con proveedor corporativo.
    Presupuesto indicativo: 180.000 EUR.
    Plazo de entrega: 8 meses desde firma de contrato.
    """

