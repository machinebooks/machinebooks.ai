# Extraído de: LibroCISO/cap-23-testing-grc.md
# tests/e2e/test_generate_dpia.py
"""E2E — Generación de DPIA conforme al Art. 35.7 RGPD."""
import pytest
from io import BytesIO
from docx import Document  # python-docx para Word


SECCIONES_ART35_7 = [
    "Descripción sistemática de las operaciones",    # Art. 35.7.a
    "Evaluación de necesidad y proporcionalidad",     # Art. 35.7.b
    "Evaluación de riesgos",                          # Art. 35.7.c
    "Medidas previstas",                              # Art. 35.7.d
]


class TestGenerarDPIA:
    """Verificar que la DPIA generada cumple Art. 35.7 RGPD."""

    @pytest.mark.e2e
    @pytest.mark.regulatory
    async def test_dpia_completa_word(
        self, client, auth_headers, tratamiento_alto_riesgo_id
    ):
        """Generar DPIA para un tratamiento de alto riesgo y verificar
        que el documento Word resultante contiene las 4 secciones
        obligatorias del Art. 35.7."""
        resp = await client.post(
            f"/api/v1/privacy/dpia/generate/{tratamiento_alto_riesgo_id}",
            params={"format": "docx"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert "application/vnd.openxmlformats" in resp.headers["content-type"]

        # Parsear el documento Word generado
        doc = Document(BytesIO(resp.content))
        texto_completo = "\n".join([p.text for p in doc.paragraphs])

        # Verificar que cada sección obligatoria existe
        for seccion in SECCIONES_ART35_7:
            assert seccion.lower() in texto_completo.lower(), (
                f"Art. 35.7: la DPIA generada no contiene la sección "
                f"'{seccion}'. El documento es incompleto para la AEPD."
            )

        # Verificar que incluye datos del tratamiento
        assert tratamiento_alto_riesgo_id is not None
        # El documento debe referenciar el tratamiento concreto
        assert "alto riesgo" in texto_completo.lower() or \
               "high risk" in texto_completo.lower()
