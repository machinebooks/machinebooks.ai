# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# Ejemplo didáctico: patrones/rag/evaluator.py
import anthropic

def evaluate_rag_response(
    question: str,
    retrieved_chunks: list[str],
    generated_answer: str,
    evaluator_model: str = "claude-haiku-4-5",  # Modelo rápido y económico para evaluación
) -> dict:
    """
    Evalúa la calidad de una respuesta RAG en cuatro dimensiones.
    Usa un modelo Claude secundario como evaluador.
    """
    client = anthropic.Anthropic()

    context = "\n---\n".join(retrieved_chunks)

    evaluation_prompt = f"""Evalúa la calidad de esta respuesta RAG en cuatro dimensiones.
Devuelve SOLO un JSON con las puntuaciones del 0.0 al 1.0 y una justificación breve.

PREGUNTA DEL USUARIO:
{question}

FRAGMENTOS RECUPERADOS:
{context}

RESPUESTA GENERADA:
{generated_answer}

Evalúa:
1. groundedness: ¿Cada afirmación de la respuesta está en los fragmentos?
2. relevance: ¿Los fragmentos recuperados son pertinentes para la pregunta?
3. completeness: ¿La respuesta cubre todo lo relevante en los fragmentos?
4. faithfulness: ¿La respuesta es fiel a lo que dicen los fragmentos sin distorsionar?

Formato de respuesta (JSON puro, sin markdown):
{{"groundedness": 0.0, "relevance": 0.0, "completeness": 0.0, "faithfulness": 0.0,
  "issues": ["lista de problemas detectados si los hay"]}}
"""

    message = client.messages.create(
        model=evaluator_model,
        max_tokens=512,
        messages=[{"role": "user", "content": evaluation_prompt}],
    )

    import json
    return json.loads(message.content[0].text)
