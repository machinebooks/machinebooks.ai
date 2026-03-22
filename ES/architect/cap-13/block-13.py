# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
    elif intent.tipo == TipoIntent.CHAT_RAG:
        respuesta_rag = rag_engine.query(
            consulta,
            colecciones=["propuestas", "historico", "catalogo"],
            usuario_id=contexto_usuario.get("user_id"),
        )
        return {
            "tipo": "rag_response",
            "motor": "qdrant+claude",
            "intent_confianza": intent.confianza,
            "datos": respuesta_rag,
        }

    elif intent.tipo == TipoIntent.WORKFLOW:
        tarea = workflow_engine.trigger(
            tipo=intent.subtipo,
            consulta_original=consulta,
            contexto=contexto_usuario,
        )
        return {
            "tipo": "workflow_triggered",
            "motor": "workflow_engine",
            "intent_confianza": intent.confianza,
            "datos": {"task_id": tarea.id, "estado": "iniciado"},
        }

    else:  # OFF_TOPIC
        return {
            "tipo": "off_topic",
            "motor": "none",
            "intent_confianza": intent.confianza,
            "datos": {
                "mensaje": "Esta consulta está fuera del ámbito de la plataforma. "
                           "Puedes buscar oportunidades, analizar documentos o "
                           "generar propuestas. ¿En qué puedo ayudarte?",
            },
        }
