// Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
// Ejemplo didáctico: componente de chat con streaming SSE
import { useRef, useState, useCallback } from "react";

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  metadata?: { agent?: string; sources?: string[] };
}

interface ModuleContext {
  module: "privacy" | "risk" | "compliance" | "breaches" | "nis2" | "dora";
  entity_type?: string;    // "treatment", "risk", "control", "breach"
  entity_id?: number;      // ID del registro que el usuario está viendo
  action?: string;         // "viewing", "editing", "creating"
}

function CopilotChat({ context }: { context: ModuleContext }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingStatus, setStreamingStatus] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);

    // Preparar mensaje del asistente vacío para ir llenándolo
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: "",
      metadata: {},
    };
    setMessages((prev) => [...prev, assistantMessage]);

    // Abrir conexión SSE
    abortRef.current = new AbortController();
    try {
      const response = await fetch("/api/v1/ai/copilot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          context,           // El módulo y registro activo
          history: messages.slice(-10),  // Últimos 10 mensajes
        }),
        signal: abortRef.current.signal,
      });

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // Parsear eventos SSE (data: {...}\n\n)
        const events = chunk.split("\n\n").filter(Boolean);

        for (const event of events) {
          if (!event.startsWith("data: ")) continue;
          const payload = JSON.parse(event.slice(6));

          switch (payload.type) {
            case "token":
              // Token de texto: añadir al mensaje del asistente
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                last.content += payload.content;
                return updated;
              });
              break;

            case "progress":
              // Evento de progreso: "Consultando RAG normativo..."
              setStreamingStatus(payload.message);
              break;

            case "sources":
              // Fuentes normativas utilizadas en la respuesta
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                last.metadata = { ...last.metadata, sources: payload.sources };
                return updated;
              });
              break;

            case "done":
              setStreamingStatus(null);
              break;
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        console.error("Error en streaming:", err);
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  }, [input, isStreaming, context, messages]);

  const cancelGeneration = () => abortRef.current?.abort();

  return (
    <div className="flex h-full flex-col border-l bg-slate-50">
      {/* Cabecera con contexto actual */}
      <div className="border-b bg-white px-4 py-3">
        <h3 className="text-sm font-semibold">Copiloto GRC</h3>
        <p className="text-xs text-slate-500">
          Contexto: {context.module}
          {context.entity_type && ` → ${context.entity_type} #${context.entity_id}`}
        </p>
      </div>

      {/* Área de mensajes */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={msg.role === "user" ? "text-right" : "text-left"}
          >
            <div
              className={`inline-block rounded-lg px-4 py-2 text-sm
                ${msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-slate-800 shadow-sm"
                }`}
            >
              {msg.content}
              {/* Fuentes normativas como badges */}
              {msg.metadata?.sources && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {msg.metadata.sources.map((s) => (
                    <span key={s} className="rounded bg-slate-100
                                             px-2 py-0.5 text-xs text-slate-600">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {/* Indicador de progreso */}
        {streamingStatus && (
          <p className="text-xs italic text-slate-400">{streamingStatus}</p>
        )}
      </div>

      {/* Entrada de texto */}
      <div className="border-t bg-white p-3">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Pregunta al copiloto..."
            className="flex-1 rounded-lg border px-3 py-2 text-sm"
            disabled={isStreaming}
          />
          {isStreaming ? (
            <button onClick={cancelGeneration}
                    className="rounded-lg bg-red-100 px-4 text-red-600">
              Cancelar
            </button>
          ) : (
            <button onClick={sendMessage}
                    className="rounded-lg bg-blue-600 px-4 text-white">
              Enviar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
