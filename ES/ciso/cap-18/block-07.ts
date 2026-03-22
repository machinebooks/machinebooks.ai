// Extraído de: LibroCISO/cap-18-react-grc.md
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],

    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@/components': path.resolve(__dirname, './src/components'),
        '@/api': path.resolve(__dirname, './src/api'),
        '@/modules': path.resolve(__dirname, './src/modules'),
        '@/stores': path.resolve(__dirname, './src/stores'),
      },
    },

    server: {
      port: 3000,
      proxy: {
        // Todo /api/* → FastAPI (evita CORS en desarrollo)
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },

    build: {
      target: 'esnext',
      sourcemap: mode === 'development',
      rollupOptions: {
        output: {
          // Code splitting por tipo de dependencia
          manualChunks: {
            'vendor-react': ['react', 'react-dom', 'react-router-dom'],
            'vendor-query': ['@tanstack/react-query', '@tanstack/react-table'],
            'vendor-ui': ['@radix-ui/react-dialog', 'lucide-react'],
            'vendor-charts': ['recharts'],
            'vendor-forms': ['react-hook-form', 'zod'],
            'vendor-i18n': ['react-i18next', 'i18next'],
          },
        },
      },
      // Alerta si un chunk supera 1 MB
      chunkSizeWarningLimit: 1000,
    },
  }
})
