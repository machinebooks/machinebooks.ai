// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// vite.config.ts — Configuración del bundler
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',       // Accesible desde la red local
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_HOST
          ? `http://${process.env.VITE_API_HOST}`
          : 'http://localhost',
        changeOrigin: true,
        secure: false,      // Acepta certificados autofirmados
      },
    },
  },
});
