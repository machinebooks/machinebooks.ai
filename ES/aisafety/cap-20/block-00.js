// Extraido de: LibroAISafety/cap-20-caso-copilot.md
// ORIGINAL (simplificado):
// function filterHandler(t) {
//   if (t.finish_reason === "content_filter") { ... bloquear ... }
// }

// MODIFICADO: se añade return; al inicio
// function filterHandler(t) {
//   return; // <-- bypass: la función nunca evalúa el filtro
//   if (t.finish_reason === "content_filter") { ... }
// }
