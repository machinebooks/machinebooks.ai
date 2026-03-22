// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        // Leemos el stream de bytes y decodificamos fragmento a fragmento
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value, { stream: true });
          // Los mensajes SSE siguen el formato "data: {...}\n\n"
          const lines = text.split('\n').filter((l) => l.startsWith('data: '));

          for (const line of lines) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') {
              setIsStreaming(false);
              options.onComplete?.(fullTextRef.current);
              return;
            }
            try {
              const parsed = JSON.parse(data);
              const chunk = parsed.text || '';
              fullTextRef.current += chunk;
              setStreamText((prev) => prev + chunk);
              options.onChunk?.(chunk);
            } catch {
              // Fragmento mal formado, continuamos
            }
          }
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setIsStreaming(false);
          options.onError?.(err.message);
        }
      } finally {
        setIsStreaming(false);
      }
    },
    [options]
  );

  return { streamText, isStreaming, startStream, stopStream };
}
