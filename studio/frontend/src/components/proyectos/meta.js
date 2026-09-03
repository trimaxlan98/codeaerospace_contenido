// Vocabulario compartido de la vista Proyectos: constantes, etiquetas de
// estado y funciones puras. Aqui NO hay JSX ni estado de React.
//
// Existe porque la lista, el detalle y la tarjeta de clip hablaban el mismo
// idioma (que es «renderizado», que es «al dia», cuanto dura un clip de este
// tipo) desde un solo archivo de 1 667 lineas. Al partirlo, ese idioma tenia
// que quedarse en UN sitio o cada pieza se habria traido su copia.

import { splitName } from '../../catalogo.js'

export const QUALITY_LABEL = { ql: '480p', qm: '720p', qh: '1080p' }

// Rango de duracion por tipo de proyecto. En un curso es el que valida
// `studio/tools/render_local.py`: un clip mas corto no alcanza a contar nada
// y uno mas largo se cae del formato. Un promo de redes juega otro juego
// (8-15 s, en bucle), y medirlo con la vara del curso marcaba en ambar todos
// los promos por estar "cortos". Aqui solo se avisa, no se bloquea nada.
export const DURACION = {
  curso: { min: 28, max: 45 },
  promo: { min: 8, max: 15 },
  // Una presentacion no tiene rango: dura lo que el ponente necesite
  // contar. El semaforo solo avisaria de nada. Se deja abierto en
  // vez de esconder la duracion, que sigue siendo util para ensayar.
  presentacion: { min: 0, max: 3600 },
}

export function rangoDuracion(tipo) {
  return DURACION[tipo] || DURACION.curso
}

export const STATUS_META = {
  rendered: { label: 'renderizado', dot: 'bg-ok', text: 'text-ok' },
  stale: { label: 'desactualizado', dot: 'bg-warn', text: 'text-warn' },
  no_render: { label: 'sin render', dot: 'bg-muted', text: 'text-muted' },
  queued: { label: 'en cola', dot: 'bg-cyan', text: 'text-cyan' },
  running: { label: 'renderizando', dot: 'bg-cyan', text: 'text-cyan' },
}

export const NARR_META = {
  al_dia: { label: 'al día', text: 'text-ok' },
  desactualizada: { label: 'desactualizada', text: 'text-warn' },
  guion: { label: 'guion sin voz', text: 'text-warn' },
  sin_narracion: { label: 'sin narración', text: 'text-muted' },
}

export function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

export function fmtDur(s) {
  if (s == null) return null
  return `${s.toFixed(1)} s`
}

export function fmtTotal(s) {
  if (!s) return '—'
  const m = Math.floor(s / 60)
  return `${m}:${String(Math.round(s - m * 60)).padStart(2, '0')}`
}

// Job en vuelo (queued/running) para un clip: hay que evitar disparar un
// segundo render mientras el primero sigue en cola o corriendo, y reflejarlo
// en el badge de estado.
export function activeJobFor(jobs, clipId) {
  return jobs.find((j) => j.clip_id === clipId && (j.status === 'queued' || j.status === 'running'))
}

// Clips stale/no_render que NO tienen ya un job en vuelo: sirve tanto para
// decidir si el boton masivo esta habilitado como para saber si hace falta
// evitar el endpoint global (que reencolaria un clip cuyo render sigue en
// curso, porque su rendered_hash aun no cambio).
export function staleWithoutActiveJob(clips, jobs) {
  return clips.filter((c) => (c.status === 'stale' || c.status === 'no_render') && !activeJobFor(jobs, c.id))
}

export const textareaCls = 'w-full resize-y rounded-md border border-line bg-canvas px-2.5 py-1.5 text-[12.5px] text-ink placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan'

// ── el indice de cursos ──────────────────────────────────────────────────

// `splitName` vive en catalogo.js: la misma etiqueta corta la usan la tira de
// la cola del Estudio y los avisos de fin de render.

export function totals(items) {
  return items.reduce((a, p) => ({
    clips: a.clips + p.clip_count,
    rendered: a.rendered + p.rendered_count,
    stale: a.stale + p.stale_count,
    narrated: a.narrated + (p.narrated_count || 0),
  }), { clips: 0, rendered: 0, stale: 0, narrated: 0 })
}

export const FILTERS = [
  { id: 'todos', label: 'Todos' },
  { id: 'pendientes', label: 'Con pendientes' },
  { id: 'completos', label: 'Completos' },
  // Solo aparece si el catalogo tiene narracion (ver `showNarr`): sin ella
  // seria un filtro que siempre devuelve todo.
  { id: 'sin_narrar', label: 'Sin narrar', narr: true },
]

export function matchesFilter(p, filter) {
  if (filter === 'completos') return p.clip_count > 0 && p.rendered_count === p.clip_count
  if (filter === 'pendientes') return p.clip_count === 0 || p.rendered_count < p.clip_count
  if (filter === 'sin_narrar') return p.clip_count > 0 && (p.narrated_count || 0) < p.clip_count
  return true
}

// Agrupa por familia. Un prefijo con un solo proyecto (p. ej. "Marca · Intro
// y cierre") no merece grupo propio: cae en "Cursos sueltos".
export function groupProjects(projects, order) {
  const byFamily = new Map()
  for (const p of projects) {
    const { family, label } = splitName(p.name)
    const key = family || ''
    if (!byFamily.has(key)) byFamily.set(key, [])
    byFamily.get(key).push({ ...p, label })
  }
  const families = []
  const loose = []
  for (const [key, items] of byFamily) {
    if (key && items.length > 1) {
      // Dentro de una familia manda el numero de leccion, no la actividad.
      families.push({ key, items: [...items].sort((a, b) => a.label.localeCompare(b.label, 'es')) })
    } else {
      loose.push(...items.map((it) => ({ ...it, label: it.name })))
    }
  }
  const byName = (a, b) => a.label.localeCompare(b.label, 'es')
  const byActivity = (a, b) => b.updated_at - a.updated_at
  loose.sort(order === 'nombre' ? byName : byActivity)
  families.sort(order === 'nombre'
    ? (a, b) => a.key.localeCompare(b.key, 'es')
    : (a, b) => Math.max(...b.items.map((p) => p.updated_at)) - Math.max(...a.items.map((p) => p.updated_at)))
  return { families, loose }
}

/** Cómo se llama lo que hay dentro de un grupo. Una familia de promos son
 *  promos, no «lecciones»: llamarlas así sería heredar la palabra del caso
 *  que ya existía. */
export function contar(items, loose) {
  const uno = items.length === 1
  if (items.every((p) => p.tipo === 'promo')) return uno ? 'promo' : 'promos'
  if (loose) return uno ? 'curso' : 'cursos'
  return uno ? 'lección' : 'lecciones'
}

export const OPEN_KEY = 'ms_projects_open'

export function readOpen() {
  try { return new Set(JSON.parse(localStorage.getItem(OPEN_KEY)) || []) }
  catch { return new Set() }
}

// ── el estilo compartido (R5a) ───────────────────────────────────────────

// Espejo de `projects.STYLE_MARKER`. El backend compone
// `style_block + MARCADOR + script` antes de renderizar, asi que el script
// que guarda un job de clip trae el estilo pegado delante: para volver a
// sacar el script DEL CLIP hay que cortar por aqui.
export const STYLE_MARKER = '# --- fin estilo del proyecto ---'

/** Script del clip dentro del script compuesto que guardo un render.
 *
 *  Sin estilo, `compose_script` devuelve el script tal cual y no hay
 *  marcador: entonces el compuesto ES el script del clip. */
export function scriptDelClip(compuesto) {
  const i = (compuesto || '').indexOf(STYLE_MARKER)
  if (i < 0) return compuesto || ''
  return compuesto.slice(i + STYLE_MARKER.length).replace(/^\r?\n\r?\n/, '')
}

/** Espejo de `projects.style_offset`: lineas que el estilo antepone al
 *  script del clip.
 *
 *  El Estudio se lo RESTA a los numeros de linea que reporta un fallo de
 *  manim, que hablan del script compuesto y no del que se esta editando.
 *  Python: `len(compose_script(style, "X").splitlines()) - 1`, o sea las
 *  lineas del estilo sin cola + linea en blanco + marcador + linea en
 *  blanco. */
export function styleOffset(styleBlock) {
  const s = styleBlock || ''
  if (!s.trim()) return 0
  return s.replace(/\s+$/, '').split('\n').length + 3
}

// ── la identidad del canal (R5a) ─────────────────────────────────────────

// Espejo de `app/branding.py`. La marca dejo de ser opcional: si el script
// compuesto no la aplica por su cuenta, ManimStudio le ANEXA el bloque de
// identidad antes de renderizar. Saberlo desde el editor de estilo evita la
// sorpresa de una marca de agua que nadie escribio.
//
// Se busca el IMPORT de `presentacion` y no la palabra suelta, igual que en
// el backend y por la misma razon: «presentacion» —o «lienzo»— en un
// comentario haria creer que el script trae marca propia y dejaria el render
// sin ella. Un falso positivo aqui es peor que no avisar.
const RE_MARCA = /code_brand/
const RE_IMPORTA_PRESENTACION = /^[ \t]*(?:import[ \t]+presentacion\b|from[ \t]+presentacion[ \t]+import\b)/m

export function traeMarca(texto) {
  return RE_MARCA.test(texto || '') || RE_IMPORTA_PRESENTACION.test(texto || '')
}

export function importaPresentacion(texto) {
  return RE_IMPORTA_PRESENTACION.test(texto || '')
}

// ── el audio de un clip (R5a) ────────────────────────────────────────────

/** Lo que la fila de audio necesita saber del manifiesto de un clip.
 *
 *  `GET /api/projects/{pid}` NO trae el manifiesto: `clip_public` quita
 *  `audio_json` a proposito (son hasta 30 clips por curso) y solo deja
 *  `audio = {estado, has_audio}`. El tema de musica y el numero de efectos
 *  hay que pedirlos con `GET .../clips/{cid}/audio`, y por eso el detalle
 *  los pide UNA vez y solo para los clips que ya tienen manifiesto. */
export function resumenAudio(manifiesto) {
  const audio = manifiesto?.audio || {}
  const musica = audio.musica || null
  return {
    tema: musica?.tema || null,
    db: musica?.db,
    efectos: (audio.eventos || []).length,
    frases: (manifiesto?.voz?.secciones || []).length,
  }
}
