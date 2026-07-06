import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Las llamadas usan rutas relativas /api — no hay URL que "hornear" en el
// build (leccion del despliegue de finanzas-app). El proxy de dev apunta al
// backend local para desarrollo.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://127.0.0.1:3002' },
  },
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: { manualChunks: { reader: ['marked', 'dompurify', 'katex'] } },
    },
  },
})
