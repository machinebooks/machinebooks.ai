// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
      fetch(`${baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return res.json();
        })
        .then(({ stream_id }) => {
          // Abrimos el EventSource con el stream_id y el token como query param
          // Nota: EventSource no permite cabeceras personalizadas; el token
          // va en la URL y el backend lo valida como parámetro de seguridad.
          // El stream_id se almacena en Redis con un TTL de 30 segundos
          // y se elimina tras la primera conexión.
          const url = `${baseUrl}/stream/${stream_id}?token=${token}`;
          const eventSource = new EventSource(url);
          eventSourceRef.current = eventSource;

          eventSource.onmessage = (event) => {
            if (event.data === '[DONE]') {
              // El servidor indica que el stream ha terminado
              eventSource.close();
              eventSourceRef.current = null;
              setIsStreaming(false);
              options.onComplete?.(fullTextRef.current);
              return;
            }

            try {
              const data = JSON.parse(event.data);
              const chunk = data.text || '';
              fullTextRef.current += chunk;
              setStreamText((prev) => prev + chunk);
              options.onChunk?.(chunk);
            } catch {
              // Fragmentos mal formados se ignoran; el stream continúa
            }
          };

          eventSource.onerror = () => {
            eventSource.close();
            eventSourceRef.current = null;
            setIsStreaming(false);
            options.onError?.('Error en la conexión del stream. Inténtalo de nuevo.');
          };
        })
        .catch((err) => {
          setIsStreaming(false);
          options.onError?.(err.message);
        });
    },
    [options]
  );

  return { streamText, isStreaming, startStream, stopStream };
}
