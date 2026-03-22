# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
def evaluate_retrieval(test_queries: list[dict]) -> dict:
    """Evalúa calidad de recuperación contra ground truth."""
    recalls = []
    filter_accuracies = []
    empty_count = 0

    for test in test_queries:
        query = test["query"]
        relevant_docs = set(test["relevant_doc_hashes"])

        results = search_knowledge(query, top_k=5)

        if not results:
            empty_count += 1
            recalls.append(0.0)
            continue

        # Recall@5
        retrieved_hashes = {
            r.get("doc_hash") for r in results if r.get("doc_hash")
        }
        recall = len(retrieved_hashes & relevant_docs) / len(relevant_docs)
        recalls.append(recall)

        # Precisión de filtros
        expected_filters = test.get("expected_filters", {})
        if expected_filters:
            correct = sum(
                1 for r in results
                if all(
                    r["metadata"].get(k) == v
                    for k, v in expected_filters.items()
                )
            )
            filter_accuracies.append(correct / len(results))

    return {
        "mean_recall_at_5": sum(recalls) / len(recalls),
        "mean_filter_precision": (
            sum(filter_accuracies) / len(filter_accuracies)
            if filter_accuracies else None
        ),
        "empty_rate": empty_count / len(test_queries),
        "total_queries": len(test_queries)
    }
