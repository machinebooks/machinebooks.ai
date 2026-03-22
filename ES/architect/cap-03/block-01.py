# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
"""
LA PLATAFORMA - Copilot Orchestrator
=====================================
Orquestador inteligente — punto único de entrada del Copilot.

Flujo:
  1. Recibe mensaje + contexto
  2. Intent Classifier decide el modo (chat_rag / agent_tools / orchestrate)
  3. Rutea al handler apropiado
  4. Streaming SSE unificado

Tres modos:
  A) Chat + RAG — respuesta directa con contexto de documentos
  B) Agent con Tools — loop agentic ReAct (plan → act → observe → reflect)
  C) Orquestador Workflow — encadena sub-pipelines como tools

SEGURIDAD (detalle en capítulo 6):
  - SecurityContext propagado a cada capa (default-DENY en acceso a colecciones)
  - Input guardrails: regex + detección semántica con Haiku
  - Output guardrails: filtrado de credenciales, rutas internas, exposición de system prompt
  - Timeout por modo (chat: 30s, agent: 120s, workflow: 300s)
  - Max iterations en loops (previene loops infinitos y consumo ilimitado de tokens)
  - Rate limiting por usuario con sliding window en Redis
"""
