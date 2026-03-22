// Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
// Ejemplo didáctico: deduplicación de mensajes
const addLogLine = (newLog: LogLine) => {
  const messageKey =
    `${newLog.timestamp}-${newLog.line}-${newLog.source}`;

  if (seenMessages.has(messageKey)) return; // Duplicado
  seenMessages.add(messageKey);

  // Limitar el set a 1000 entradas para evitar fuga de memoria
  if (seenMessages.size > 1000) {
    const keys = Array.from(seenMessages);
    const trimmed = new Set(keys.slice(-800));
    // ... reemplazar set
  }

  setLogs(prev => [...prev, newLog]);
};
