// Router por hash minimo: la vista activa (y un parametro opcional) viven en
// la URL — #/estudio, #/aprender/<id>, #/renders, #/laboratorio, #/admin/<tab>
// — para que F5 conserve la vista, atras/adelante navegue y haya deep-links.

import { useCallback, useEffect, useState } from 'react'
import { getPrefs } from './prefs.js'

// Hash canonico de cada vista (el que se escribe en la URL).
const VIEW_TO_HASH = {
  studio: 'estudio',
  projects: 'proyectos',
  renders: 'renders',
  entregas: 'biblioteca',
  learn: 'aprender',
  lab: 'laboratorio',
  admin: 'admin',
  settings: 'configuracion',
}

// Hash -> vista. Incluye los ALIAS de antes del sprint 4, cuando Aprender y
// Animaciones eran dos secciones y los renders se llamaban Biblioteca: los
// enlaces guardados (y el hash que el navegador aun tenga en la barra al
// desplegar) siguen abriendo la vista que toca.
const HASH_TO_VIEW = {
  ...Object.fromEntries(Object.entries(VIEW_TO_HASH).map(([v, h]) => [h, v])),
  animaciones: 'learn',
  // `#/biblioteca` apuntaba a los renders cuando esa pestaña se llamaba asi
  // (antes del sprint 4). Desde la Biblioteca de entregas el nombre vuelve a
  // significar lo que dice: las entregas. Los renders siguen en `#/renders`.
  entregas: 'entregas',
}

export function parseHash(hash = window.location.hash) {
  const [seg, ...rest] = hash.replace(/^#\/?/, '').split('/')
  const view = HASH_TO_VIEW[seg]
  // Sin hash manda la preferencia "vista al abrir" (Configuracion); con un
  // hash que no existe, el Estudio. Un enlace directo siempre gana: la
  // preferencia solo decide cuando nadie ha dicho a donde ir.
  if (!view) return { view: seg ? 'studio' : getPrefs().landing, param: null }
  return { view, param: rest.length ? rest.map(decodeURIComponent).join('/') : null }
}

export function hashFor(view, param = null) {
  const base = `#/${VIEW_TO_HASH[view] || 'estudio'}`
  return param
    ? `${base}/${String(param).split('/').map(encodeURIComponent).join('/')}`
    : base
}

export function useRoute() {
  const [route, setRoute] = useState(parseHash)

  useEffect(() => {
    const onChange = () => setRoute(parseHash())
    window.addEventListener('hashchange', onChange)
    // Primera carga sin hash: fijar la vista de inicio sin crear entrada de
    // historial (la ruta ya la resolvio parseHash con la preferencia).
    if (!window.location.hash) {
      window.history.replaceState(null, '', hashFor(parseHash().view))
    }
    return () => window.removeEventListener('hashchange', onChange)
  }, [])

  const navigate = useCallback((view, param = null) => {
    const target = hashFor(view, param)
    if (window.location.hash !== target) window.location.hash = target
  }, [])

  return [route, navigate]
}
