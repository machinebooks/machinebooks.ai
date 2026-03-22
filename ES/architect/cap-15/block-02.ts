// Extraído de: LibroTecnico/cap-15-interfaces-chat.md
import { useState, useRef, useCallback } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
}

export function useChatStream(chatContext: ChatContext) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (userMessage: string) => {
    // 1. Añadir mensaje del usuario al historial local
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: userMessage
    };

    // 2. Añadir mensaje vacío del asistente (se irá rellenando)
    const assistantMsgId = crypto.randomUUID();
    setMessages(prev => [...prev, userMsg, {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      isStreaming: true
    }]);

    setIsStreaming(true);
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/ai/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          history: messages.map(m => ({ role: m.role, content: m.content })),
          context: chatContext
        }),
        signal: abortControllerRef.current.signal
      });

      // 3. Leer el stream token a token
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        // Parsear líneas SSE (formato: "data: {...}\n\n")
        const lines = chunk.split('\n').filter(l => l.startsWith('data: '));

        for (const line of lines) {
          const event = JSON.parse(line.slice(6));

          if (event.type === 'delta') {
            // Actualizar el contenido del mensaje en streaming
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMsgId
                ? { ...msg, content: msg.content + event.content }
                : msg
            ));
          } else if (event.type === 'done') {
            // Marcar como completado y registrar uso de tokens
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMsgId
                ? { ...msg, isStreaming: false }
                : msg
            ));
          }
        }
      }
    } finally {
      setIsStreaming(false);
    }
  }, [messages, chatContext]);

  const stopStreaming = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  return { messages, isStreaming, sendMessage, stopStreaming };
}
