// Extraído de: LibroPQC/cap-20-chat-ia.md
const handleSend = async () => {
  if (!input.trim() || loading) return

  const userMessage = input.trim()
  setInput('')
  setCurrentAction(null)

  // Añadir mensaje del usuario inmediatamente (UX)
  const newMessages = [...messages, { role: 'user', content: userMessage }]
  setMessages(newMessages)
  setLoading(true)

  try {
    const config = { model, provider }
    if (customUrl) config.base_url = customUrl

    // Construir historial (últimos 10 intercambios)
    const history = newMessages.slice(1).map(m => ({
      role: m.role, content: m.content
    }))

    // Ruta 1: modo agente con repositorio disponible
    if (agentMode && repoCachePath) {
      await handleAgentMessage(userMessage, history, config)
    }
    // Ruta 2: chat simple con contexto opcional
    else {
      await handleSimpleMessage(userMessage, history, config)
    }
  } catch (err) {
    setError(err.response?.data?.error || err.message)
    setMessages(messages) // Revertir el mensaje del usuario
  }

  setLoading(false)
}
