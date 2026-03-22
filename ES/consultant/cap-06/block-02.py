# Extraído de: LibroConsultor/cap-06-generacion-entregables.md
    def generate_full_report(self, assessment_data: dict) -> str:
        """Pipeline completo de tres fases."""
        # Fase 1: Esquema global
        outline = self._generate_outline(assessment_data)

        # Fase 2: Generación por secciones
        sections_content = {}
        total_tokens = 0
        for section in self.template["sections"]:
            if section.get("static_content"):
                sections_content[section["id"]] = (
                    self._get_static_content(section["id"])
                )
                continue
            result = self.generate_section(
                section, assessment_data, outline
            )
            sections_content[section["id"]] = result.content
            total_tokens += result.tokens_used
            self.results.append(result)

        # Fase 3: Revisión de coherencia
        assembled = self._assemble_document(sections_content)
        coherent = self._review_coherence(assembled)

        # Registrar metadatos de generación
        self._save_metadata(assessment_data, total_tokens)
        return coherent

    def _generate_outline(self, data: dict) -> str:
        """Fase 1: esquema con hallazgos principales."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""A partir de estos datos de assessment,
genera un esquema del informe con:
1. Los 5 hallazgos más críticos
2. El porcentaje de cumplimiento global
3. El tono general (alarmante/preocupante/aceptable)
4. Las 3 recomendaciones prioritarias

Datos: {self._summarize_data(data)}"""
            }]
        )
        return response.content[0].text
