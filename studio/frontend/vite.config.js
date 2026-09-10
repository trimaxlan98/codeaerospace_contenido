import { defineConfig } from 'vite'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Las llamadas usan rutas relativas /api — no hay URL que "hornear" en el
// build (leccion del despliegue de finanzas-app). El proxy de dev apunta al
// backend local para desarrollo.
// El backend local puede no estar en 3002 (una instancia de QA levanta la
// suya aparte): MS_API_PROXY la redirige sin tocar el archivo.
const API = process.env.MS_API_PROXY || 'http://127.0.0.1:3002'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: { '/api': API },
  },
  // `vite preview` sirve el `dist/` real (el que se despliega) y necesita el
  // mismo proxy: es como se audita la interfaz compilada contra un backend
  // local (ver studio/tools/ux_instancia.py).
  preview: {
    proxy: { '/api': API },
  },
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: { manualChunks: { reader: ['marked', 'dompurify', 'katex'] } },
    },
  },
})
