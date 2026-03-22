// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// vite.config.ts para la App Analytics (subpath /analytics)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/analytics/',  // Todas las referencias a assets usarán /analytics/ como prefijo
  build: {
    outDir: 'dist',
    // Genera un manifest.json útil para debugging de assets en producción
    manifest: true,
  },
  server: {
    // En desarrollo, el proxy redirige las llamadas a la API al backend local
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/ai': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, ''),
      },
    },
  },
});
