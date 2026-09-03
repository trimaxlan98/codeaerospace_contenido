// Preferencias de la interfaz.
//
// Viven en localStorage: ManimStudio es de un solo usuario y el backend no
// guarda perfil, asi que un ajuste es del navegador que lo fija. No valen
// useState locales porque la misma preferencia la leen varias piezas a la vez
// (la cabecera, el fondo animado, los avisos de fin de render) y cambiarla en
// Configuracion tiene que repintarlas al instante — de ahi el store con
// suscripcion sobre useSyncExternalStore.
//
// El tema NO esta aqui: lo lee `index.html` antes del primer pintado para
// evitar el destello, asi que sigue siendo su propia clave (`themes.js`).

import { useSyncExternalStore } from 'react'

const KEY = 'ms_prefs'

export const DEFAULTS = {
  landing: 'studio',   // vista al abrir la app sin hash
  motion: 'auto',      // auto (respeta prefers-reduced-motion) | off
  toasts: true,        // avisos de fin de render
  telemetry: true,     // CPU/RAM/reloj UTC en la cabecera
  // Ayudas para quien no escribe Manim a mano (asistente de clip). APAGADO
  // por defecto y sin excepciones: con `guided: false` la app no enseña ni un
  // boton de mas que antes de existir esta preferencia. Quien programa no
  // tiene que apagar nada; quien lo necesita lo enciende aqui.
  guided: false,
}

// Ids de vista validos como pantalla de inicio (el mismo orden de la nav).
export const LANDING_VIEWS = [
  { id: 'projects', label: 'Proyectos' },
  { id: 'studio', label: 'Estudio' },
  { id: 'renders', label: 'Renders' },
  { id: 'learn', label: 'Aprender' },
  { id: 'lab', label: 'Laboratorio' },
  { id: 'admin', label: 'Admin' },
]

// El sprint 4 fusiono Animaciones en Aprender y renombro Biblioteca a
// Renders. Una preferencia guardada con el id viejo se traduce en vez de
// caer al valor por defecto sin explicacion.
const LANDING_ALIAS = { library: 'renders', lessons: 'learn', animations: 'learn' }

function read() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '{}')
    const out = { ...DEFAULTS }
    for (const k of Object.keys(DEFAULTS)) {
      if (raw[k] !== undefined && typeof raw[k] === typeof DEFAULTS[k]) out[k] = raw[k]
    }
    out.landing = LANDING_ALIAS[out.landing] || out.landing
    if (!LANDING_VIEWS.some((v) => v.id === out.landing)) out.landing = DEFAULTS.landing
    if (!['auto', 'off'].includes(out.motion)) out.motion = DEFAULTS.motion
    return out
  } catch {
    return { ...DEFAULTS } // localStorage puede fallar (modo privado, cuota)
  }
}

let cache = read()
const subs = new Set()

function emit() {
  for (const fn of subs) fn()
}

function subscribe(fn) {
  subs.add(fn)
  return () => subs.delete(fn)
}

export function getPrefs() {
  return cache
}

export function setPref(key, value) {
  if (!(key in DEFAULTS)) return
  cache = { ...cache, [key]: value }
  try { localStorage.setItem(KEY, JSON.stringify(cache)) } catch { /* no critico */ }
  emit()
}

/** Lee una preferencia y re-renderiza al cambiarla desde cualquier vista. */
export function usePref(key) {
  return useSyncExternalStore(subscribe, () => cache[key], () => DEFAULTS[key])
}

/** true cuando la animacion debe correr: la preferencia manda, y en `auto`
 *  decide el sistema operativo (`prefers-reduced-motion`). */
export function motionAllowed(pref = cache.motion) {
  if (pref === 'off') return false
  return !window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
}

// Todo lo que la app guarda en este navegador, para poder enseñarlo y
// borrarlo desde Configuracion en vez de tener que abrir las devtools.
export const LOCAL_KEYS = [
  { key: 'ms_theme', label: 'Tema elegido' },
  { key: KEY, label: 'Preferencias de la interfaz' },
  { key: 'ms_studio_script', label: 'Script del editor' },
  { key: 'ms_studio_scene', label: 'Escena seleccionada' },
  { key: 'ms_studio_quality', label: 'Calidad del Estudio' },
  { key: 'ms_studio_timeout', label: 'Timeout del Estudio' },
  { key: 'ms_lessons_read', label: 'Lecciones marcadas como leidas' },
  { key: 'ms_projects_open', label: 'Familias desplegadas en Proyectos' },
]

export function localUsage() {
  return LOCAL_KEYS.map((k) => {
    let value = null
    try { value = localStorage.getItem(k.key) } catch { /* sin acceso */ }
    return { ...k, present: value != null, bytes: value ? value.length : 0 }
  })
}

/** Borra lo guardado por la app en este navegador. `keep` permite conservar
 *  el trabajo del editor, que es lo unico irrecuperable de la lista. */
export function clearLocal(keep = []) {
  for (const { key } of LOCAL_KEYS) {
    if (keep.includes(key)) continue
    try { localStorage.removeItem(key) } catch { /* no critico */ }
  }
  cache = read()
  emit()
}
