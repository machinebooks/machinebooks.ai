// Extraído de: LibroPQC/cap-20-chat-ia.md
const handleAgentMessage = async (userMessage, history, config) => {
  setCurrentAction({ type: 'thinking', message: 'Analizando solicitud...' })

  const response = await sendAgentMessage(
    userMessage,
    repoCachePath,
    history.slice(-10),
    provider,
    config,
    false // streaming desactivado por defecto
  )

  // Procesar eventos para mostrar acciones
  const actions = []
  if (response.events) {
    for (const event of response.events) {
      if (event.type === 'tool_call') {
        setCurrentAction({
          type: 'tool',
          tool: event.tool,
          args: event.args,
          message: `${toolNames[event.tool] || event.tool}...`
        })
        actions.push({ type: 'call', tool: event.tool, args: event.args })
      } else if (event.type === 'tool_result') {
        actions.push({
          type: 'result', tool: event.tool,
          success: event.success, result: event.result
        })
      }
    }
  }

  // Añadir respuesta del asistente con metadatos
  setMessages(prev => [...prev, {
    role: 'assistant',
    content: response.response,
    provider: response.provider,
    model: response.model,
    actions: response.actions || [],
    iterations: response.iterations
  }])
}
