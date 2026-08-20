// Catalogo de cursos: una sola copia del indice de proyectos para toda la app.
//
// Hasta el sprint 8 tres piezas pedian `GET /api/projects` por su cuenta y no
// compartian nada: el indice de Proyectos, la lista de Renders (para poder
// decir de que curso es cada video) y el dialogo "añadir a un proyecto".
// Cambiar de vista volvia a bajar los ~60 cursos, y las piezas que NO pedian
// el indice —la tira de la cola del Estudio y los avisos de fin de render—
// se quedaban sin el dato: un clip terminado se anunciaba como «Clip3», que
// no dice de que curso es ni cual de los ~300 clips del catalogo es.
//
// Aqui vive una vez, con suscripcion (mismo patron que `prefs.js`), y quien
// muta proyectos llama a `refreshCatalogo()`.

import { useEffect, useSyncExternalStore } from 'react'
import { api } from './api.js'

const VACIO = { list: [], byId: {}, loaded: false, error: '' }

let cache = VACIO
let inflight = null
const subs = new Set()

function emit(next) {
  cache = next
  for (const fn of subs) fn()
}

function subscribe(fn) {
  subs.add(fn)
  return () => subs.delete(fn)
}

function getSnapshot() {
  return cache
}

/** Descarga el indice si hace falta. Varias vistas montandose a la vez
 *  comparten la misma peticion (`inflight`). */
export function loadCatalogo(force = false) {
  if (inflight) return inflight
  if (cache.loaded && !force) return Promise.resolve(cache)
  inflight = api.listProjects()
    .then((d) => {
      const list = d.projects || []
      emit({ list, byId: Object.fromEntries(list.map((p) => [p.id, p])), loaded: true, error: '' })
      return cache
    })
    .catch((err) => {
      // `loaded` sigue en false a proposito: un fallo (tipico: 401 mientras
      // se pinta el login) no puede dejar el catalogo vacio para siempre —
      // el proximo que lo pida vuelve a intentarlo.
      emit({ ...cache, error: err.message })
      return cache
    })
    .finally(() => { inflight = null })
  return inflight
}

/** Tras crear/borrar un proyecto o un clip: vuelve a pedir el indice. */
export function refreshCatalogo() {
  return loadCatalogo(true)
}

/** Estado del catalogo, cargandolo la primera vez que alguien lo mira.
 *  `enabled` existe para el shell: pedir el indice sin sesion solo produce un
 *  401 inutil, y hay que volver a pedirlo cuando la sesion aparece. */
export function useCatalogo(enabled = true) {
  const snap = useSyncExternalStore(subscribe, getSnapshot, () => VACIO)
  useEffect(() => { if (enabled) loadCatalogo() }, [enabled])
  return snap
}

const FAMILY_SEP = ' · '

/** "Metrología óptica · 1.1 La luz como regla" → familia + etiqueta corta. */
export function splitName(name) {
  const i = name.indexOf(FAMILY_SEP)
  if (i < 0) return { family: null, label: name }
  return { family: name.slice(0, i), label: name.slice(i + FAMILY_SEP.length) }
}

/** De que curso es un render, si lo es. Devuelve `null` para el render libre
 *  del Estudio (la mayoria de los jobs SI son clips de un curso).
 *  `label` es la etiqueta corta dentro de la familia — con 18 lecciones de
 *  Algebra lineal en catalogo, repetir la familia en cada ficha es ruido. */
export function cursoDeJob(job, catalogo) {
  const p = job?.project_id ? catalogo.byId[job.project_id] : null
  if (!p) return null
  const { family, label } = splitName(p.name)
  return { id: p.id, name: p.name, family, label }
}
