import React from 'react'
import ReactDOM from 'react-dom/client'
import '@fontsource-variable/inter'
import '@fontsource-variable/space-grotesk'
import '@fontsource-variable/jetbrains-mono'
import './theme.css'   // sistema de diseño (Tailwind v4 + tokens)
import './styles.css'  // legacy: vistas aun no migradas (Biblioteca/Aprender/Admin)
import App from './App.jsx'
import { currentTheme, applyTheme } from './themes.js'

// Aplica el tema guardado antes del primer render para evitar parpadeo.
applyTheme(currentTheme())

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
