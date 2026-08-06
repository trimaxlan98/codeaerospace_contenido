// Router por hash minimo: la vista activa (y un parametro opcional) viven en
// la URL — #/estudio, #/aprender/<id>, #/animaciones/<id>, #/admin/<tab> —
// para que F5 conserve la vista, atras/adelante navegue y haya deep-links.

import { useCallback, useEffect, useState } from 'react'

const HASH_TO_VIEW = {
  estudio: 'studio',
  proyectos: 'projects',
  biblioteca: 'library',
  aprender: 'lessons',
  animaciones: 'animations',
  admin: 'admin',
}
const VIEW_TO_HASH = Object.fromEntries(
  Object.entries(HASH_TO_VIEW).map(([h, v]) => [v, h]),
)

export function parseHash(hash = window.location.hash) {
  const [seg, ...rest] = hash.replace(/^#\/?/, '').split('/')
  const view = HASH_TO_VIEW[seg]
  if (!view) return { view: 'studio', param: null }
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
    // Primera carga sin hash: fijar #/estudio sin crear entrada de historial.
    if (!window.location.hash) window.history.replaceState(null, '', hashFor('studio'))
    return () => window.removeEventListener('hashchange', onChange)
  }, [])

  const navigate = useCallback((view, param = null) => {
    const target = hashFor(view, param)
    if (window.location.hash !== target) window.location.hash = target
  }, [])

  return [route, navigate]
}
