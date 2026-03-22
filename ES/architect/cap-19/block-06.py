# Extraído de: LibroTecnico/cap-19-testing-ia.md
    def test_analysis_meets_rag_quality_profile(self):
        """
        Verifica que el análisis documental produce outputs que cumplen
        el perfil de calidad definido para la categoría 'analysis'.
        """
        # Llamada real al modelo
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Analiza el siguiente documento de requisitos y proporciona:
1. Resumen ejecutivo (3-5 líneas)
2. Recomendación GO/NO-GO con justificación
3. Principales factores de riesgo
4. Requisitos clave identificados

Documento:
{self.TEST_DOCUMENT}"""
            }]
        )

        output = response.content[0].text

