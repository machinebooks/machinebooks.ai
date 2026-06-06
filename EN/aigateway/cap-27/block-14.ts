// Extracted from: LibroAIGateway/cap-27-frontend-architecture-realtime.md
// Consumption in any component or hook
window.addEventListener('n7x:realtime', (e: CustomEvent) => {
  if (e.detail.type === 'quota_exceeded') {
    // React to the event
  }
});
