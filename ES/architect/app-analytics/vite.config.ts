// Extraído de: LibroTecnico/cap-16-react-ia.md
// app-analytics/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  base: '/analytics/',          // Ruta base en Nginx
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, '../shared'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,           // Desactivado en producción
    rollupOptions: {
      output: {
        // Separación manual de chunks para evitar bundle único enorme
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'charts': ['recharts'],
          'query': ['@tanstack/react-query'],
        },
      },
    },
  },
  server: {
    port: 3001,                 // Puerto distinto por aplicación en dev
    proxy: {
      '/api': 'http://localhost:5000',
      '/analytics-api': 'http://localhost:5000',
    },
  },
})
