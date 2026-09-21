import { EditorView } from '@codemirror/view'
import { HighlightStyle, defaultHighlightStyle, syntaxHighlighting } from '@codemirror/language'
import { useSyncExternalStore } from 'react'

// Temas: conjuntos de variables CSS aplicados via data-theme en <html>.
// Curados a 4 (antes 7) para no diluir la identidad. 'orbital' = :root.
// swatch = [lienzo, acento, secundario] para la muestra del selector.

export const THEMES = [
  { id: 'orbital', name: 'Liquid Glass', swatch: ['#030712', '#00d8f6', '#3b82f6'] },
  { id: 'ion', name: 'Emerald Glass', swatch: ['#020c08', '#10b981', '#34d399'] },
  { id: 'nebula', name: 'Nebula Glass', swatch: ['#07020d', '#df5ff2', '#b06cf8'] },
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
  return CLAROS.has(useThemeId()) ? TEMA_EDITOR_CLARO : 'dark'
}

// El resaltado claro por defecto de CodeMirror (`defaultHighlightStyle`) trae
// tres colores por debajo de AA sobre el panel de `daylight` (sprint 11, la
// auditoria por pixel lo cazo en las f-strings del Laboratorio): el naranja
// de f-strings y regex `#e40` (3,06:1 sobre #e1e6eb), el verde de tipos
// `#085` (3,59:1) y el rojo de lo invalido `#f00` (3,18:1). Se oscurecen
// dentro de su familia; el resto de la paleta ya pasaba de 5:1.
//
// Tiene que ser el estilo ENTERO y no solo esos tres: en CodeMirror 6, en
// cuanto hay un resaltador que no es `fallback`, los `fallback` (el de
// basicSetup) se ignoran por completo.
const OSCURECER = { '#e40': '#b83300', '#085': '#06703d', '#f00': '#b91c1c' }
const TEMA_EDITOR_CLARO = [
  EditorView.theme({}, { dark: false }),
  syntaxHighlighting(HighlightStyle.define(defaultHighlightStyle.specs.map(
    (spec) => (OSCURECER[spec.color] ? { ...spec, color: OSCURECER[spec.color] } : spec)))),
]
