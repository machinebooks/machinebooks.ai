# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
def answer_query(query: str) -> dict:
    """Pipeline RAG completo: búsqueda + generación con fuentes."""
    results = search_knowledge(query, top_k=5)

    if not results:
        return {
            "answer": "No encontré documentos relevantes para esta consulta.",
            "sources": []
        }

    # Construir contexto con fuentes numeradas
    context_parts = []
    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        source_label = (
            f"[Fuente {i}: {meta['tipo']} — {meta['sector']} "
            f"— {meta.get('framework', 'general')} — {meta['year']}]"
        )
        context_parts.append(f"{source_label}\n{r['text']}")

    context = "\n\n---\n\n".join(context_parts)

    response = client_anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            "Eres un asistente de conocimiento para una consultora tecnológica. "
            "Responde basándote EXCLUSIVAMENTE en el contexto proporcionado. "
            "Cita las fuentes usando [Fuente N]. "
            "Si el contexto no contiene información suficiente, dilo. "
            "NO inventes información que no esté en las fuentes."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Contexto de la base de conocimiento:\n\n{context}\n\n"
                f"---\n\nPregunta del consultor: {query}"
            )
        }]
    )
    return {
        "answer": response.content[0].text,
        "sources": [
            {
                "tipo": r["metadata"]["tipo"],
                "sector": r["metadata"]["sector"],
                "year": r["metadata"]["year"],
                "score": round(r["score"], 3),
                "section": r["section"]
            }
            for r in results
        ]
    }
