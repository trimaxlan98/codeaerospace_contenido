import { useSyncExternalStore } from 'react'

// Temas: conjuntos de variables CSS aplicados via data-theme en <html>.
// Curados a 4 (antes 7) para no diluir la identidad. 'orbital' = :root.
// swatch = [lienzo, acento, secundario] para la muestra del selector.

export const THEMES = [
  { id: 'orbital', name: 'Liquid Glass', swatch: ['#030712', '#00d8f6', '#3b82f6'] },
  { id: 'ion', name: 'Emerald Glass', swatch: ['#020c08', '#10b981', '#34d399'] },
  { id: 'nebula', name: 'Nebula Glass', swatch: ['#07020d', '#d946ef', '#a855f7'] },
  // Unico tema claro: la muestra debe enseñar su lienzo real (#f1f5f9), no
  // uno oscuro — con el swatch anterior parecia otro tema oscuro mas.
  // `light` no es decorativo: lo consulta `useEditorTheme` para que CodeMirror
  // no pinte una paleta oscura sobre el lienzo claro.
  { id: 'daylight', name: 'Ice Glass', swatch: ['#f1f5f9', '#0369a1', '#1d4ed8'], light: true },
]

export function currentTheme() {
  const saved = localStorage.getItem('ms_theme')
  return THEMES.some((t) => t.id === saved) ? saved : 'orbital'
}

export function applyTheme(id) {
  document.documentElement.dataset.theme = id
  localStorage.setItem('ms_theme', id)
}

// ── El tema activo, como store ────────────────────────────────────────────
// La fuente de verdad es `data-theme` en <html>, no un estado de React:
// `index.html` lo escribe antes del primer pintado para evitar el destello, y
// `applyTheme` lo cambia despues. Quien necesite reaccionar al tema se
// suscribe al atributo (mismo patron que StarfieldBackground).
const CLAROS = new Set(THEMES.filter((t) => t.light).map((t) => t.id))

function suscribirTema(alCambiar) {
  const obs = new MutationObserver(alCambiar)
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
  return () => obs.disconnect()
}

const leerTema = () => document.documentElement.dataset.theme || 'orbital'

export function useThemeId() {
  return useSyncExternalStore(suscribirTema, leerTema, () => 'orbital')
}

/** Tema de CodeMirror que toca al tema activo.
 *
 *  Sin esto el editor iba con `theme="dark"` fijo mientras `.cm-editor` tiene
 *  `background: transparent`, asi que en `daylight` pintaba la paleta One Dark
 *  sobre un panel casi blanco: entre 1,60:1 y 3,07:1 segun el token. El
 *  editor —el nucleo del Estudio— era ilegible en el unico tema claro. */
export function useEditorTheme() {
  return CLAROS.has(useThemeId()) ? 'light' : 'dark'
}
