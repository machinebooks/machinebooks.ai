# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
    def triage_document(self, doc_name: str, doc_content: str) -> dict:
        """Clasifica un documento por relevancia y dominio."""
        # Usar claude-haiku-4-5 para triaje: rápido y económico
        response = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"""Clasifica este documento para una auditoría {self.framework}.

Documento: {doc_name}
Contenido (primeras 2.000 palabras): {doc_content[:8000]}

Responde SOLO en JSON:
{{
  "relevant": true/false,
  "domain": "seguridad|cumplimiento|procesos|arquitectura|otro",
  "controls_related": ["lista de IDs de controles posiblemente relacionados"],
  "summary": "resumen en una frase"
}}"""
            }]
        )
        return json.loads(response.content[0].text)

    def ingest_documents(self, docs_folder: str):
        """Ingesta y triaje de todos los documentos."""
        docs_path = Path(docs_folder)
        triaged = {"relevant": 0, "discarded": 0}

        for doc_file in docs_path.glob("**/*.*"):
            if doc_file.suffix.lower() in (".pdf", ".docx", ".md", ".txt"):
                content = self._extract_text(doc_file)
                classification = self.triage_document(doc_file.name, content)

                if classification["relevant"]:
                    self.documents[doc_file.name] = content
                    triaged["relevant"] += 1
                else:
                    triaged["discarded"] += 1

        print(f"Triaje: {triaged['relevant']} relevantes, "
              f"{triaged['discarded']} descartados")
