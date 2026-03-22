# Extraído de: LibroDevSecOps/cap-16-data-poisoning-rag.md
class SecureRAGSystem:
    """Orquestación completa del pipeline RAG seguro."""

    def __init__(self, config: dict):
        api_key = config["anthropic_api_key"]
        self.ingestion = SecureIngestionPipeline()
        self.semantic_validator = SemanticDocumentValidator(api_key)
        self.retriever = SecureRAGRetriever(
            config["qdrant_url"], config["collection"]
        )
        self.injection_detector = IndirectInjectionDetector(
            anthropic.Anthropic(api_key=api_key)
        )
        self.llm = anthropic.Anthropic(api_key=api_key)

    def ingest_document(
        self, text: str, metadata: DocumentMetadata
    ) -> dict:
        """Ingesta segura: estática + semántica + indexación."""
        # Capa 1: validación estática
        static_result = self.ingestion.validate_static(
            text, metadata
        )
        if not static_result.passed:
            return {
                "status": "rejected",
                "stage": "static",
                "findings": static_result.findings
            }

        # Capa 2: validación semántica
        semantic_result = self.semantic_validator.validate(
            text, domain_context="normativa de seguridad"
        )
        if not semantic_result.passed:
            return {
                "status": "rejected",
                "stage": "semantic",
                "findings": semantic_result.findings
            }

        # Capa 3: indexar con metadatos de seguridad
        metadata.validation_status = "approved"
        metadata.ingested_at = datetime.now(
            timezone.utc
        ).isoformat()
        metadata.validation_notes = (
            static_result.findings + semantic_result.findings
        )
        self._index_with_metadata(text, metadata)

        return {
            "status": "indexed",
            "sha256": metadata.sha256,
            "risk_score": max(
                static_result.risk_score,
                semantic_result.risk_score
            )
        }

    def query(self, question: str, user: UserContext) -> dict:
        """Consulta segura: retrieval filtrado + generación + validación."""
        # Paso 1: recuperar chunks con control de acceso
        chunks = self.retriever.retrieve(
            question, user, top_k=5
        )

        if not chunks:
            return {
                "answer": "No se encontraron documentos relevantes "
                          "para su nivel de acceso.",
                "sources": [],
                "security_status": "no_results"
            }

        # Paso 2: generar respuesta con contexto
        context = "\n\n".join(
            [c["text"] for c in chunks]
        )
        response = self.llm.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=(
                "Responde basándote exclusivamente en el contexto "
                "proporcionado. Si el contexto no contiene información "
                "suficiente, indícalo. No inventes datos."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Contexto:\n{context}\n\n"
                    f"Pregunta: {question}"
                )
            }]
        )
        answer = response.content[0].text

        # Paso 3: validar respuesta contra inyección indirecta
        check = self.injection_detector.check_response(
            question,
            [c["text"] for c in chunks],
            answer
        )

        if check["action"] == "block":
            return {
                "answer": "La respuesta no superó los controles de "
                          "integridad. Consulte con el administrador.",
                "sources": [c["source"] for c in chunks],
                "security_status": "blocked",
                "security_details": check["concerns"]
            }

        return {
            "answer": answer,
            "sources": [c["source"] for c in chunks],
            "security_status": check["action"],
            "coherence_score": check["coherence_score"]
        }

    def _index_with_metadata(
        self, text: str, metadata: DocumentMetadata
    ):
        """Indexa documento con metadatos de seguridad."""
        # Chunking, embedding e inserción en Qdrant
        # (simplificado — en producción usar langchain/llama_index)
        pass
