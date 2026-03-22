# Extraído de: LibroTecnico/cap-12-rag-produccion.md
    def format_docs_with_sources(docs):
        """Formatea los documentos recuperados incluyendo el ID como referencia."""
        return "\n\n---\n\n".join(
            f"[Documento ID: {doc.metadata.get('document_id', 'N/A')}] "
            f"Tipo: {doc.metadata.get('document_type', 'N/A')}\n"
            f"{doc.page_content}"
            for doc in docs
        )

    chain = (
        {
            "context": vectorstore_retriever | format_docs_with_sources,
            "question": RunnablePassthrough(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return chain
