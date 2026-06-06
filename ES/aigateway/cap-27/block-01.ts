// Extraído de: LibroAIGateway/cap-27-frontend-arquitectura-realtime.md
// admin-panel/vite.config.ts — build del admin
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',           // admin → dist/
    rollupOptions: { input: './index.html' },  // entry: src/main.tsx
  },
});
