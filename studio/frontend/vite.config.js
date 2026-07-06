import { defineConfig } from 'vite'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Las llamadas usan rutas relativas /api — no hay URL que "hornear" en el
// build (leccion del despliegue de finanzas-app). El proxy de dev apunta al
// backend local para desarrollo.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
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
