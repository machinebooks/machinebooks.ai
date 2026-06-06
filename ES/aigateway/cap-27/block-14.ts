// Extraído de: LibroAIGateway/cap-27-frontend-arquitectura-realtime.md
// Consumo en cualquier componente o hook
window.addEventListener('n7x:realtime', (e: CustomEvent) => {
  if (e.detail.type === 'quota_exceeded') {
    // Reaccionar al evento
  }
});
