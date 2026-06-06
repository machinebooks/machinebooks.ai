# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/services/semantic_cache_service.py:4-7 (docstring)
"""
Disenado para purposes seguros (chat, quick_qa, translate, summarize) donde
una pregunta con redaccion similar puede legitimamente compartir respuesta.
NO activar en orchestradores (documento, evaluar, propuesta): cross-poisoning entre
secciones similares puede devolver respuestas erroneas.
"""
