# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# Ejemplo didáctico: patrones/rag/rag_chain.py
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def build_rag_chain(
    vectorstore_retriever,
    model_name: str = "claude-sonnet-4-6",
    max_tokens: int = 2048,
) -> dict:
    """
    Construye la cadena RAG completa: recuperación + síntesis con Claude.
    Devuelve respuesta con fuentes citadas y flag de suficiencia del contexto.
    """
    llm = ChatAnthropic(
        model=model_name,
        max_tokens=max_tokens,
        temperature=0.1,  # Baja temperatura para respuestas factuales
    )

    # Prompt diseñado para minimizar alucinación y forzar citas de fuente
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un asistente especializado que responde preguntas
basándote EXCLUSIVAMENTE en los fragmentos de documentos proporcionados.

Reglas estrictas:
1. Solo usa información que aparezca explícitamente en los fragmentos.
2. Si la información no está en los fragmentos, indica claramente que no
   dispones de esa información en los documentos consultados.
3. Cita siempre el documento fuente entre corchetes: [Documento ID: {doc_id}].
4. No extrapoles ni inferas información que no esté en el texto.
5. Si los fragmentos son contradictorios, indica la contradicción al usuario.

Fragmentos de documentos disponibles:
{context}
"""),
        ("human", "{question}"),
    ])

