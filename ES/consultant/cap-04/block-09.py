# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
def chunk_audit_report(text: str) -> list[dict]:
    """Chunking especializado para informes de auditoría."""
    findings = extract_findings(text)  # detecta patrón de hallazgos
    chunks = []

    for finding in findings:
        # Cada hallazgo incluye control, evidencia y recomendación
        chunk_text = (
            f"Control: {finding['control']}\n"
            f"Estado: {finding['status']}\n"
            f"Evidencia: {finding['evidence']}\n"
            f"Hallazgo: {finding['finding']}\n"
            f"Recomendación: {finding['recommendation']}"
        )
        chunks.append({
            "text": chunk_text,
            "section": f"Hallazgo — {finding['control']}",
            "chunk_type": "audit_finding"
        })

    return chunks
