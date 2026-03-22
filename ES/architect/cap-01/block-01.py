# Extraído de: LibroTecnico/cap-01-cambio-ocurrio.md
import anthropic
import hashlib
import time

# Patrón didáctico: orquestación de análisis documental con Claude
# Muestra las tres capas que separan un prototipo de un sistema de producción:
# 1) Recuperación de contexto (RAG), 2) Guardrails, 3) Trazabilidad

client = anthropic.Anthropic()

def analizar_documento_requisitos(
    contenido_documento: str,
    proyecto_id: int,
    usuario_id: int,
    prompt_version: str = "v3.2"
) -> dict:
    """Analiza un documento de requisitos con Claude, integrando RAG y trazabilidad."""

    # 1. Recuperar contexto relevante del RAG (Qdrant)
    fragmentos_similares = buscar_contexto_rag(
        query=contenido_documento[:2000],  # Primeras líneas como query
        coleccion="documentos_requisitos",
        proyecto_id=proyecto_id,           # Filtrar por proyecto activo
        top_k=5
    )
    contexto_rag = "\n---\n".join([f.texto for f in fragmentos_similares])

    # 2. Guardrail de entrada: verificar que no hay PII sin anonimizar
    pii_detectada = detectar_pii(contenido_documento)
    if pii_detectada:
        contenido_documento = anonimizar_campos(contenido_documento, pii_detectada)

    # 3. Cargar prompt versionado desde base de datos (no hardcodeado)
    prompt_sistema = cargar_prompt("document_analysis_main", version=prompt_version)

    # 4. Llamada al modelo con trazabilidad completa
    inicio = time.time()
    respuesta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=prompt_sistema,
        messages=[{
            "role": "user",
            "content": f"Documento a analizar:\n{contenido_documento}\n\n"
                       f"Contexto de propuestas similares:\n{contexto_rag}"
        }]
    )
    duracion_ms = int((time.time() - inicio) * 1000)

    # 5. Registro de auditoría: cada llamada queda trazada
    registrar_uso_llm(
        modelo="claude-sonnet-4-6",
        tipo_tarea="analisis_documental",
        usuario_id=usuario_id,
        tokens_entrada=respuesta.usage.input_tokens,
        tokens_salida=respuesta.usage.output_tokens,
        latencia_ms=duracion_ms,
        prompt_version=prompt_version,
        hash_entrada=hashlib.sha256(contenido_documento.encode()).hexdigest()
    )

    return {
        "analisis": respuesta.content[0].text,
        "fragmentos_rag_usados": len(fragmentos_similares),
        "pii_anonimizada": bool(pii_detectada),
        "latencia_ms": duracion_ms
    }
