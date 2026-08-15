// Proyectos (cursos): agrupan clips ordenados con continuidad narrativa y
// estilo compartido.
//
// La lista NO es una rejilla plana: el catalogo real son ~60 proyectos y la
// mayoria pertenece a una *familia* (Aerodinamica 1.1…4.5, Electromagnetismo
// 1.1…4.3, Metrologia optica 1.1…3.3), que en el nombre se escribe
// "Familia · N.M Titulo". Por eso la lista es un indice: familias plegables
// con su progreso agregado, buscador y filtro por estado.
//
// El detalle muestra lo que el pipeline necesita mirar de un vistazo: estado
// de render por clip, DURACION del video (el formato pide 28-45 s) y estado
// de narracion.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  ChevronDown, ChevronRight, ChevronUp, Download, FileJson, FileText,
  FolderKanban, Film, Layers, Mic, Pencil, Plus, RefreshCw, Search, Square, Wand2,
} from 'lucide-react'
import { api, narracionAudioUrl, projectArchiveUrl, projectExportUrl, thumbUrl } from './api.js'
import { PLANTILLAS, plantillaPorId } from './plantillas.js'
import { usePref } from './prefs.js'
import ClipAssistant from './components/ClipAssistant.jsx'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select.jsx'
import DeleteButton from './components/DeleteButton.jsx'
import { cn } from '@/lib/utils'

const QUALITY_LABEL = { ql: '480p', qm: '720p', qh: '1080p' }

// Mismo rango que valida `studio/tools/render_local.py` (DURACION_MIN/MAX):
// un clip mas corto no alcanza a contar nada y uno mas largo se cae del
// formato. Aqui solo se avisa, no se bloquea nada.
const DURACION_MIN = 28
const DURACION_MAX = 45

const STATUS_META = {
  rendered: { label: 'renderizado', dot: 'bg-ok', text: 'text-ok' },
  stale: { label: 'desactualizado', dot: 'bg-warn', text: 'text-warn' },
  no_render: { label: 'sin render', dot: 'bg-muted', text: 'text-muted' },
  queued: { label: 'en cola', dot: 'bg-cyan', text: 'text-cyan' },
  running: { label: 'renderizando', dot: 'bg-cyan', text: 'text-cyan' },
}

const NARR_META = {
  al_dia: { label: 'al día', text: 'text-ok' },
  desactualizada: { label: 'desactualizada', text: 'text-warn' },
  sin_narracion: { label: 'sin narración', text: 'text-muted' },
}

function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

function fmtDur(s) {
  if (s == null) return null
  return `${s.toFixed(1)} s`
}

function fmtTotal(s) {
  if (!s) return '—'
  const m = Math.floor(s / 60)
  return `${m}:${String(Math.round(s - m * 60)).padStart(2, '0')}`
}

// Job en vuelo (queued/running) para un clip: hay que evitar disparar un
// segundo render mientras el primero sigue en cola o corriendo, y reflejarlo
// en el badge de estado.
function activeJobFor(jobs, clipId) {
  return jobs.find((j) => j.clip_id === clipId && (j.status === 'queued' || j.status === 'running'))
}

// Clips stale/no_render que NO tienen ya un job en vuelo: sirve tanto para
// decidir si el boton masivo esta habilitado como para saber si hace falta
// evitar el endpoint global (que reencolaria un clip cuyo render sigue en
// curso, porque su rendered_hash aun no cambio).
function staleWithoutActiveJob(clips, jobs) {
  return clips.filter((c) => (c.status === 'stale' || c.status === 'no_render') && !activeJobFor(jobs, c.id))
}

const textareaCls = 'w-full resize-y rounded-md border border-line bg-canvas px-2.5 py-1.5 text-[12.5px] text-ink placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan'

export default function Projects({ jobs, onEditClip, routeId, onRoute, aiEnabled }) {
  if (routeId) {
    return (
      <ProjectDetail key={routeId} projectId={routeId} jobs={jobs} aiEnabled={aiEnabled}
        onEditClip={onEditClip} onBack={() => onRoute(null)} />
    )
  }
  return <ProjectsList onOpen={(id) => onRoute(id)} />
}

// ── indice de cursos ─────────────────────────────────────────────────────

const FAMILY_SEP = ' · '

// "Metrología óptica · 1.1 La luz como regla" → familia + etiqueta corta.
function splitName(name) {
  const i = name.indexOf(FAMILY_SEP)
  if (i < 0) return { family: null, label: name }
  return { family: name.slice(0, i), label: name.slice(i + FAMILY_SEP.length) }
}

function totals(items) {
  return items.reduce((a, p) => ({
    clips: a.clips + p.clip_count,
    rendered: a.rendered + p.rendered_count,
    stale: a.stale + p.stale_count,
  }), { clips: 0, rendered: 0, stale: 0 })
}

const FILTERS = [
  { id: 'todos', label: 'Todos' },
  { id: 'pendientes', label: 'Con pendientes' },
  { id: 'completos', label: 'Completos' },
]

function matchesFilter(p, filter) {
  if (filter === 'completos') return p.clip_count > 0 && p.rendered_count === p.clip_count
  if (filter === 'pendientes') return p.clip_count === 0 || p.rendered_count < p.clip_count
  return true
}

// Agrupa por familia. Un prefijo con un solo proyecto (p. ej. "Marca · Intro
// y cierre") no merece grupo propio: cae en "Cursos sueltos".
function groupProjects(projects, order) {
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

// Barra de progreso de render: verde lo vigente, ambar lo desactualizado.
function ProgressBar({ rendered, stale, total, className }) {
  if (!total) return null
  const pctOk = (rendered / total) * 100
  const pctStale = (stale / total) * 100
  return (
    <div className={cn('h-1.5 overflow-hidden rounded-full bg-canvas', className)}
      role="progressbar" aria-valuenow={rendered} aria-valuemin={0} aria-valuemax={total}
      aria-label={`${rendered} de ${total} clips renderizados`}>
      <div className="flex h-full">
        <span className="block h-full bg-ok" style={{ width: `${pctOk}%` }} />
        <span className="block h-full bg-warn" style={{ width: `${pctStale}%` }} />
      </div>
    </div>
  )
}

function CountsLine({ t }) {
  return (
    <>
      {t.clips} clip{t.clips === 1 ? '' : 's'} · {t.rendered} listo{t.rendered === 1 ? '' : 's'}
      {t.stale > 0 && <span className="text-warn"> · {t.stale} desactualizado{t.stale === 1 ? '' : 's'}</span>}
      {t.clips - t.rendered - t.stale > 0 && (
        <span className="text-muted"> · {t.clips - t.rendered - t.stale} sin render</span>
      )}
    </>
  )
}

const OPEN_KEY = 'ms_projects_open'

function readOpen() {
  try { return new Set(JSON.parse(localStorage.getItem(OPEN_KEY)) || []) }
  catch { return new Set() }
}

function ProjectsList({ onOpen }) {
  const [projects, setProjects] = useState(null)
  const [error, setError] = useState('')
  const [newOpen, setNewOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('todos')
  const [order, setOrder] = useState('actividad')
  const [openFamilies, setOpenFamilies] = useState(readOpen)

  const load = useCallback(() => {
    setError('')
    api.listProjects().then((d) => setProjects(d.projects)).catch((err) => setError(err.message))
  }, [])

  useEffect(() => { load() }, [load])

  const toggleFamily = (key) => {
    setOpenFamilies((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key); else next.add(key)
      try { localStorage.setItem(OPEN_KEY, JSON.stringify([...next])) } catch { /* no critico */ }
      return next
    })
  }

  const remove = async (id) => {
    setError('')
    try {
      await api.deleteProject(id)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const q = query.trim().toLowerCase()
  const visible = useMemo(() => (projects || []).filter((p) => (
    matchesFilter(p, filter)
    && (!q || `${p.name} ${p.description || ''}`.toLowerCase().includes(q))
  )), [projects, filter, q])
  const { families, loose } = useMemo(() => groupProjects(visible, order), [visible, order])
  const all = totals(visible)
  // Buscando o filtrando, plegar esconderia justo lo que se busca.
  const forceOpen = Boolean(q) || filter !== 'todos'

  return (
    <main data-view="projects" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="proyectos">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Proyectos</span>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-faint" />
              <Input type="search" value={query} onChange={(e) => setQuery(e.target.value)}
                placeholder="Buscar curso…" aria-label="buscar proyectos"
                className="h-8 w-[190px] pl-8 text-[13px]" />
            </div>
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="h-8 w-[150px]" aria-label="filtrar por estado"><SelectValue /></SelectTrigger>
              <SelectContent>
                {FILTERS.map((f) => <SelectItem key={f.id} value={f.id}>{f.label}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={order} onValueChange={setOrder}>
              <SelectTrigger className="h-8 w-[130px]" aria-label="ordenar"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="actividad">Actividad</SelectItem>
                <SelectItem value="nombre">Nombre</SelectItem>
              </SelectContent>
            </Select>
            <Button size="sm" variant="primary" onClick={() => setNewOpen(true)}>
              <Plus className="h-3.5 w-3.5" /> Nuevo proyecto
            </Button>
          </div>
        </div>

        {projects != null && projects.length > 0 && (
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 border-b border-line px-3 py-2 text-[12px] text-muted">
            <span className="font-mono text-[11px] text-faint">
              {visible.length}/{projects.length} proyecto{projects.length === 1 ? '' : 's'}
              {families.length > 0 && ` · ${families.length} familia${families.length === 1 ? '' : 's'}`}
            </span>
            <span className="text-faint">·</span>
            <span><CountsLine t={all} /></span>
            <ProgressBar rendered={all.rendered} stale={all.stale} total={all.clips}
              className="ml-auto w-full max-w-[220px]" />
          </div>
        )}

        {projects == null ? (
          <p className="p-4 text-[13px] text-muted">Cargando proyectos…</p>
        ) : projects.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">
            Sin proyectos todavía. Crea uno para agrupar clips en un curso con continuidad.
          </p>
        ) : visible.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">
            Ningún curso coincide con la búsqueda o el filtro.
          </p>
        ) : (
          <div className="flex flex-col">
            {families.map((f) => (
              <FamilyGroup key={f.key} name={f.key} items={f.items}
                open={forceOpen || openFamilies.has(f.key)}
                onToggle={() => toggleFamily(f.key)}
                onOpen={onOpen} onDelete={remove} />
            ))}
            {loose.length > 0 && (
              families.length === 0 ? (
                <ProjectGrid items={loose} onOpen={onOpen} onDelete={remove} />
              ) : (
                <FamilyGroup name="Cursos sueltos" items={loose} loose
                  open={forceOpen || openFamilies.has('__sueltos__')}
                  onToggle={() => toggleFamily('__sueltos__')}
                  onOpen={onOpen} onDelete={remove} />
              )
            )}
          </div>
        )}

        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      <NewProjectDialog open={newOpen} onOpenChange={setNewOpen}
        onCreated={(p) => { setNewOpen(false); load(); onOpen(p.id) }} />
    </main>
  )
}

function FamilyGroup({ name, items, loose, open, onToggle, onOpen, onDelete }) {
  const t = totals(items)
  return (
    <section aria-label={name} className="border-b border-line last:border-b-0">
      <button onClick={onToggle} aria-expanded={open}
        className="flex w-full items-center gap-2.5 px-3 py-2.5 text-left transition-colors hover:bg-surface-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
        {open
          ? <ChevronDown className="h-4 w-4 shrink-0 text-accent" />
          : <ChevronRight className="h-4 w-4 shrink-0 text-muted" />}
        {loose
          ? <FolderKanban className="h-4 w-4 shrink-0 text-muted" />
          : <Layers className="h-4 w-4 shrink-0 text-accent" />}
        <span className="truncate font-display text-[14.5px] font-semibold text-ink">{name}</span>
        <span className="shrink-0 font-mono text-[11px] text-faint">
          {items.length}{' '}
          {loose
            ? (items.length === 1 ? 'curso' : 'cursos')
            : (items.length === 1 ? 'lección' : 'lecciones')}
        </span>
        <span className="ml-auto hidden shrink-0 text-[12px] text-muted sm:block"><CountsLine t={t} /></span>
        <ProgressBar rendered={t.rendered} stale={t.stale} total={t.clips} className="w-20 shrink-0" />
      </button>
      {open && <ProjectGrid items={items} onOpen={onOpen} onDelete={onDelete} />}
    </section>
  )
}

function ProjectGrid({ items, onOpen, onDelete }) {
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-3 p-3.5 pt-1">
      {items.map((p) => (
        <ProjectCard key={p.id} project={p} onOpen={() => onOpen(p.id)} onDelete={() => onDelete(p.id)} />
      ))}
    </div>
  )
}

function ProjectCard({ project, onOpen, onDelete }) {
  const t = { clips: project.clip_count, rendered: project.rendered_count, stale: project.stale_count }
  return (
    <article className="group flex flex-col gap-2 overflow-hidden rounded-lg border border-line bg-surface-2 p-3 transition-colors hover:border-accent/50">
      <button onClick={onOpen}
        className="flex flex-col gap-1.5 rounded-md text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
        <h3 className="truncate font-display text-[14px] font-semibold text-ink" title={project.name}>
          {project.label || project.name}
        </h3>
        {project.description && (
          <p className="line-clamp-2 text-[12px] text-muted">{project.description}</p>
        )}
        <p className="text-[11.5px] text-muted"><CountsLine t={t} /></p>
        <ProgressBar rendered={t.rendered} stale={t.stale} total={t.clips} />
        <p className="font-mono text-[11px] text-faint">
          {QUALITY_LABEL[project.quality] || project.quality} · {fmtDate(project.updated_at)}
        </p>
      </button>
      {/* Borrar solo al pasar por encima (o con foco de teclado): con ~60
          tarjetas en pantalla, un boton destructivo permanente en cada una es
          ruido y riesgo. */}
      <div className="mt-auto flex justify-end opacity-0 transition-opacity focus-within:opacity-100 group-hover:opacity-100">
        <DeleteButton onDelete={onDelete} />
      </div>
    </article>
  )
}

// Plantillas: el selector arranca SIEMPRE en "En blanco", que reproduce el
// comportamiento de este dialogo antes de que existieran. Quien ya sabe lo
// que hace no paga ni un clic; quien no, se ahorra las ~90 lineas de estilo
// que todos los cursos del repo repiten palabra por palabra.
function NewProjectDialog({ open, onOpenChange, onCreated }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [quality, setQuality] = useState('qm')
  const [styleBlock, setStyleBlock] = useState('')
  const [plantilla, setPlantilla] = useState('blanco')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')

  useEffect(() => {
    if (open) {
      setName(''); setDescription(''); setQuality('qm'); setStyleBlock('')
      setPlantilla('blanco'); setError(''); setBusy('')
    }
  }, [open])

  const elegir = (id) => {
    setPlantilla(id)
    // La calidad de la plantilla es una sugerencia: el campo sigue editable.
    setQuality(plantillaPorId(id).quality)
  }

  const tpl = plantillaPorId(plantilla)

  const submit = async (e) => {
    e.preventDefault()
    if (!name.trim() || busy) return
    setBusy('proyecto')
    setError('')
    try {
      const built = tpl.build({ nombre: name.trim() })
      const p = await api.createProject({
        name: name.trim(),
        description,
        quality,
        // El textarea manda si el usuario escribio algo en el.
        style_block: styleBlock || built.styleBlock,
      })
      // Los clips de la plantilla van despues, en orden: si uno falla, el
      // proyecto ya existe y se dice cual quedo a medias en vez de perderlo.
      for (const [i, c] of built.clips.entries()) {
        setBusy(`clips ${i + 1}/${built.clips.length}`)
        await api.createClip(p.id, c)
      }
      onCreated(p)
    } catch (err) {
      setError(err.message)
      setBusy('')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Nuevo proyecto</DialogTitle>
            </div>
            <div className="flex flex-col gap-3 overflow-y-auto p-4">
              <div className="flex flex-col gap-1.5">
                <span className="eyebrow">Empezar desde</span>
                <div role="radiogroup" aria-label="plantilla"
                  className="grid grid-cols-[repeat(auto-fit,minmax(170px,1fr))] gap-2">
                  {PLANTILLAS.map((p) => {
                    const on = p.id === plantilla
                    return (
                      <button key={p.id} type="button" role="radio" aria-checked={on}
                        onClick={() => elegir(p.id)}
                        className={cn(
                          'flex flex-col gap-1 rounded-lg border p-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                          on ? 'border-accent bg-surface-2' : 'border-line hover:border-line-strong',
                        )}>
                        <span className={cn('text-[13px] font-semibold', on ? 'text-accent' : 'text-ink')}>
                          {p.nombre}
                        </span>
                        <span className="text-[11.5px] leading-snug text-muted">{p.resumen}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Nombre</span>
                <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus required maxLength={120} />
                <span className="text-[11.5px] text-faint">
                  Para una lección de una familia usa «Familia · 1.1 Título»: la lista
                  agrupa los cursos por ese prefijo.
                </span>
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Descripción</span>
                <Input value={description} onChange={(e) => setDescription(e.target.value)} />
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Calidad</span>
                <Select value={quality} onValueChange={setQuality}>
                  <SelectTrigger className="max-w-[180px]"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ql">480p</SelectItem>
                    <SelectItem value="qm">720p</SelectItem>
                    <SelectItem value="qh">1080p</SelectItem>
                  </SelectContent>
                </Select>
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Estilo compartido (opcional)</span>
                <textarea value={styleBlock} onChange={(e) => setStyleBlock(e.target.value)} rows={5}
                  placeholder={tpl.id === 'blanco'
                    ? 'Código Python que se antepone a cada clip (imports, colores, helpers…)'
                    : 'Vacío = el estilo de la plantilla. Escribe aquí para reemplazarlo.'}
                  className={cn(textareaCls, 'font-mono')} />
                {tpl.id !== 'blanco' && !styleBlock && (
                  <span className="text-[11.5px] text-faint">
                    La plantilla pondrá el tema oficial CO.DE Academy y creará {tpl.clips} clips
                    («{tpl.clips === 4 ? 'Clip1…Clip4' : 'Clip1…Clip8'}») con un arranque que ya
                    renderiza. Todo es editable después.
                  </span>
                )}
              </label>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={Boolean(busy) || !name.trim()}>
                {busy === 'proyecto' ? 'Creando…' : busy ? `Creando ${busy}…` : 'Crear'}
              </Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}

// ── detalle ──────────────────────────────────────────────────────────────

function ProjectDetail({ projectId, jobs, onEditClip, onBack, aiEnabled }) {
  const [project, setProject] = useState(null)
  const [narracion, setNarracion] = useState(null)
  const [error, setError] = useState('')
  const [styleOpen, setStyleOpen] = useState(false)
  const [addClipOpen, setAddClipOpen] = useState(false)
  const [assistantOpen, setAssistantOpen] = useState(false)
  // Modo guiado apagado (el valor por defecto) = esta vista es exactamente la
  // de siempre: ni el boton del asistente se monta.
  const guided = usePref('guided')
  const [guionClip, setGuionClip] = useState(null) // clip cuyo guion se lee
  const savedRef = useRef({ name: '', description: '' })
  const savedClipsRef = useRef({})
  const prevJobsRef = useRef([])

  const load = useCallback(() => {
    setError('')
    api.getProject(projectId).then((p) => {
      setProject(p)
      savedRef.current = { name: p.name, description: p.description }
      savedClipsRef.current = Object.fromEntries(
        p.clips.map((c) => [c.id, { title: c.title, scene: c.scene, final_state: c.final_state, notes: c.notes }]),
      )
    }).catch((err) => setError(err.message))
  }, [projectId])

  useEffect(() => { load() }, [load])

  const loadNarracion = useCallback(() => {
    api.getNarracion(projectId).then(setNarracion).catch(() => setNarracion(null))
  }, [projectId])

  useEffect(() => { loadNarracion() }, [loadNarracion])

  // `run` es GLOBAL (una sola narracion a la vez en toda la app): hay que
  // distinguir la corrida de ESTE proyecto de la de otro. Antes se tomaba
  // cualquier corrida como propia, asi que un proyecto ajeno mostraba
  // "Narrando 3/9…" y su boton Cancelar abortaba el trabajo del otro.
  const run = narracion?.run && !narracion.run.finished ? narracion.run : null
  const narrRun = run && run.project_id === projectId ? run : null
  const runAjena = run && run.project_id !== projectId ? run : null

  // Mientras hay una narracion en curso (propia o ajena, porque libera el
  // unico turno) se sondea el estado cada 3 s; el resultado durable vive en
  // estado.json del backend, esto es solo progreso.
  useEffect(() => {
    if (!run) return
    const t = setInterval(loadNarracion, 3000)
    return () => clearInterval(t)
  }, [run != null, loadNarracion]) // eslint-disable-line react-hooks/exhaustive-deps

  // Refresco cuando un job ligado a un clip de este proyecto pasa a estado
  // terminal (p.ej. termina un render disparado desde aqui): se compara con
  // el estado previo de `jobs`, igual que el patron de App.jsx con jobsRef.
  useEffect(() => {
    const prevJobs = prevJobsRef.current
    prevJobsRef.current = jobs
    const clipIds = new Set((project?.clips || []).map((c) => c.id))
    if (clipIds.size === 0) return
    const becameTerminal = jobs.some((j) => {
      if (!j.clip_id || !clipIds.has(j.clip_id)) return false
      const wasActive = prevJobs.find((p) => p.id === j.id)?.status
      const terminal = j.status !== 'queued' && j.status !== 'running'
      return terminal && (wasActive === 'queued' || wasActive === 'running')
    })
    if (becameTerminal) { load(); loadNarracion() }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- solo reacciona a cambios de `jobs`
  }, [jobs])

  const updateClipLocal = (cid, patch) => {
    setProject((p) => (p ? { ...p, clips: p.clips.map((c) => (c.id === cid ? { ...c, ...patch } : c)) } : p))
  }

  const onFieldChange = (cid, field, value) => updateClipLocal(cid, { [field]: value })

  const onFieldBlur = async (cid, field) => {
    const clip = project?.clips.find((c) => c.id === cid)
    const saved = savedClipsRef.current[cid]
    if (!clip || !saved || clip[field] === saved[field]) return
    try {
      const updated = await api.patchClip(project.id, cid, { [field]: clip[field] })
      if (field === 'scene' || field === 'script') {
        // clip_public no devuelve status/stale recalculados: el hash de
        // contenido incluye la escena, asi que hay que recargar el proyecto
        // completo para que el badge refleje el nuevo estado del backend.
        await load()
      } else {
        savedClipsRef.current[cid] = { ...saved, [field]: updated[field] }
        updateClipLocal(cid, { [field]: updated[field], updated_at: updated.updated_at })
      }
    } catch (err) {
      setError(err.message)
      updateClipLocal(cid, { [field]: saved[field] }) // revertir
    }
  }

  const saveName = async () => {
    if (!project || project.name === savedRef.current.name) return
    if (!project.name.trim()) { setProject((p) => ({ ...p, name: savedRef.current.name })); return }
    try {
      const updated = await api.patchProject(project.id, { name: project.name })
      savedRef.current.name = updated.name
      setProject((p) => ({ ...p, name: updated.name, updated_at: updated.updated_at }))
    } catch (err) {
      setError(err.message)
      setProject((p) => ({ ...p, name: savedRef.current.name }))
    }
  }

  const saveDescription = async () => {
    if (!project || project.description === savedRef.current.description) return
    try {
      const updated = await api.patchProject(project.id, { description: project.description })
      savedRef.current.description = updated.description
      setProject((p) => ({ ...p, description: updated.description, updated_at: updated.updated_at }))
    } catch (err) {
      setError(err.message)
      setProject((p) => ({ ...p, description: savedRef.current.description }))
    }
  }

  const move = async (cid, position) => {
    setError('')
    try {
      const { clips } = await api.moveClip(project.id, cid, position)
      setProject((p) => ({ ...p, clips }))
      savedClipsRef.current = Object.fromEntries(
        clips.map((c) => [c.id, { title: c.title, scene: c.scene, final_state: c.final_state, notes: c.notes }]),
      )
    } catch (err) {
      setError(err.message)
    }
  }

  const removeClip = async (cid) => {
    setError('')
    try {
      await api.deleteClip(project.id, cid)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const renderClip = async (cid) => {
    setError('')
    try {
      await api.renderClip(project.id, cid)
    } catch (err) {
      setError(err.message)
    }
  }

  const renderAllStale = async () => {
    setError('')
    const allStale = project.clips.filter((c) => c.status === 'stale' || c.status === 'no_render')
    const pending = staleWithoutActiveJob(project.clips, jobs)
    if (pending.length === 0) return
    try {
      if (pending.length === allStale.length) {
        // Ningun clip stale tiene job en vuelo: el endpoint masivo es seguro.
        const res = await api.renderStale(project.id)
        if (res.skipped?.length) {
          setError(`Algunos clips no se pudieron encolar: ${res.skipped.map((s) => s.error).join('; ')}`)
        }
      } else {
        // Hay clips stale con job en vuelo: el endpoint masivo re-evalua el
        // status en el momento y volveria a encolar ese clip (su
        // rendered_hash aun no cambio mientras el render sigue en curso).
        // Disparamos renders individuales solo para los que no tienen job
        // activo, en secuencia, igual que hace el flujo de `skipped`.
        const skipped = []
        for (const c of pending) {
          try {
            await api.renderClip(project.id, c.id)
          } catch (err) {
            skipped.push({ error: err.message })
          }
        }
        if (skipped.length) {
          setError(`Algunos clips no se pudieron encolar: ${skipped.map((s) => s.error).join('; ')}`)
        }
      }
    } catch (err) {
      setError(err.message)
    }
  }

  const generarNarracion = async (body = {}) => {
    setError('')
    try {
      await api.startNarracion(project.id, body)
      loadNarracion()
    } catch (err) {
      setError(err.message)
    }
  }

  const cancelarNarracion = async () => {
    setError('')
    try {
      await api.cancelNarracion(project.id)
      loadNarracion()
    } catch (err) {
      setError(err.message)
    }
  }

  const openInStudio = async (clip) => {
    setError('')
    try {
      const { script, style_offset } = await api.getClipScript(project.id, clip.id)
      onEditClip({
        projectId: project.id,
        projectName: project.name,
        clipId: clip.id,
        clipTitle: clip.title,
        quality: project.quality,
        styleOffset: style_offset,
      }, script, clip.scene)
    } catch (err) {
      setError(err.message)
    }
  }

  if (!project) {
    return (
      <main data-view="projects" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
        <section className="panel shrink-0 p-4">
          <Button size="xs" variant="ghost" onClick={onBack}>← Proyectos</Button>
          <p className="mt-2 text-[13px] text-muted">
            {error ? <span role="alert" className="text-warn">{error}</span> : 'Cargando proyecto…'}
          </p>
        </section>
      </main>
    )
  }

  const clips = [...project.clips].sort((a, b) => a.position - b.position)
  const renderedCount = clips.filter((c) => c.status === 'rendered').length
  // Cuenta solo los stale/no_render sin job en vuelo: coherente con lo que
  // "Re-renderizar desactualizados" realmente va a encolar.
  const staleCount = staleWithoutActiveJob(clips, jobs).length
  const narrByClip = Object.fromEntries((narracion?.clips || []).map((c) => [c.clip_id, c]))
  const narrPending = (narracion?.clips || []).filter((c) => c.estado !== 'al_dia').length
  const narrAlDia = (narracion?.clips || []).filter((c) => c.estado === 'al_dia').length
  const narrErrores = (narracion?.run?.finished && narracion.run.errores) || []

  // Duraciones: el pipeline pide 28-45 s por clip. Se leen del estado de
  // narracion, que ya calcula `video_s` del mp4 vigente de cada clip.
  const duraciones = clips.map((c) => narrByClip[c.id]?.video_s).filter((s) => s != null)
  const totalDur = duraciones.reduce((a, s) => a + s, 0)
  const fueraRango = duraciones.filter((s) => s < DURACION_MIN || s > DURACION_MAX).length
  const { family, label } = splitName(project.name)

  return (
    <main data-view="projects" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="cabecera del proyecto">
        <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
          <Button size="xs" variant="ghost" onClick={onBack}>← Proyectos</Button>
          {family && <span className="truncate font-mono text-[11px] text-accent">{family}</span>}
          <span className="font-mono text-[11px] text-faint">
            {clips.length} clip{clips.length === 1 ? '' : 's'}
          </span>
        </div>

        <div className="flex flex-col gap-3 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex min-w-0 flex-1 flex-col gap-1.5">
              <Input value={project.name} onChange={(e) => setProject((p) => ({ ...p, name: e.target.value }))}
                onBlur={saveName} aria-label="nombre del proyecto"
                className="h-auto max-w-md border-transparent bg-transparent px-0 font-display text-lg font-semibold text-ink hover:border-line focus-visible:border-line focus-visible:bg-canvas focus-visible:px-2" />
              <Input value={project.description || ''}
                onChange={(e) => setProject((p) => ({ ...p, description: e.target.value }))}
                onBlur={saveDescription} placeholder="Descripción (opcional)" aria-label="descripción del proyecto"
                className="h-auto max-w-lg border-transparent bg-transparent px-0 text-[13px] text-muted hover:border-line focus-visible:border-line focus-visible:bg-canvas focus-visible:px-2" />
            </div>
            <span className="shrink-0 rounded-md border border-accent/40 px-2.5 py-1 font-mono text-[11px] uppercase tracking-wide text-accent">
              {QUALITY_LABEL[project.quality] || project.quality}
            </span>
          </div>

          {/* Panel de estado del curso: lo que hay que mirar antes de exportar. */}
          <div className="grid grid-cols-[repeat(auto-fit,minmax(120px,1fr))] gap-2">
            <Stat label="Render" value={`${renderedCount}/${clips.length}`}
              tone={renderedCount === clips.length && clips.length > 0 ? 'ok' : 'warn'}
              detail={staleCount > 0 ? `${staleCount} por rehacer` : 'todo vigente'} />
            <Stat label="Duración" value={fmtTotal(totalDur)}
              tone={fueraRango > 0 ? 'warn' : 'ok'}
              detail={duraciones.length < clips.length
                ? `${duraciones.length}/${clips.length} medidos`
                : fueraRango > 0 ? `${fueraRango} fuera de ${DURACION_MIN}-${DURACION_MAX} s` : `${DURACION_MIN}-${DURACION_MAX} s por clip`} />
            <Stat label="Narración" value={narracion ? `${narrAlDia}/${clips.length}` : '—'}
              tone={narracion && narrAlDia === clips.length && clips.length > 0 ? 'ok' : 'muted'}
              detail={narracion?.voz || (narracion?.enabled === false ? 'sin Vertex' : '…')} />
          </div>

          <div className="flex flex-wrap gap-1.5">
            <Button size="sm" variant="default" asChild>
              <a href={projectExportUrl(project.id)} target="_blank" rel="noreferrer">
                <FileJson className="h-3.5 w-3.5" /> Exportar manifest
              </a>
            </Button>
            {renderedCount > 0 ? (
              <Button size="sm" variant="default" asChild>
                <a href={projectArchiveUrl(project.id)} download={`${project.name || 'curso'}.zip`}>
                  <Download className="h-3.5 w-3.5" /> Descargar curso (.zip)
                </a>
              </Button>
            ) : (
              <Button size="sm" variant="default" disabled title="Ningún clip renderizado todavía">
                <Download className="h-3.5 w-3.5" /> Descargar curso (.zip)
              </Button>
            )}
            <Button size="sm" variant="default" onClick={renderAllStale} disabled={staleCount === 0}
              title={staleCount === 0 ? 'no hay clips desactualizados sin un render en curso' : undefined}>
              <RefreshCw className="h-3.5 w-3.5" /> Re-renderizar desactualizados{staleCount > 0 ? ` (${staleCount})` : ''}
            </Button>
            {narrRun ? (
              <>
                <Button size="sm" variant="default" disabled>
                  <Mic className="h-3.5 w-3.5 animate-pulse" /> Narrando {Math.min(narrRun.done + 1, narrRun.total)}/{narrRun.total}…
                </Button>
                <Button size="sm" variant="ghost" onClick={cancelarNarracion}>
                  <Square className="h-3.5 w-3.5" /> Cancelar narración
                </Button>
              </>
            ) : (
              <Button size="sm" variant="default" onClick={() => generarNarracion()}
                disabled={!narracion?.enabled || narrPending === 0 || Boolean(runAjena)}
                title={!narracion?.enabled
                  ? 'requiere el asistente IA (Vertex) configurado'
                  : runAjena
                    ? 'hay una narración en curso en otro proyecto (solo una a la vez)'
                    : (narrPending === 0 ? 'la narración de todos los clips está al día' : undefined)}>
                <Mic className="h-3.5 w-3.5" /> Generar narración{narrPending > 0 ? ` (${narrPending})` : ''}
              </Button>
            )}
            <Button size="sm" variant="default" onClick={() => setStyleOpen(true)}>
              <Pencil className="h-3.5 w-3.5" /> Editar estilo
            </Button>
          </div>
        </div>

        {runAjena && (
          <p role="status" className="border-t border-line bg-cyan/10 px-3 py-1.5 text-[12.5px] text-cyan">
            Hay una narración en curso en otro proyecto ({runAjena.done}/{runAjena.total}).
            Solo se genera una a la vez; este proyecto tendrá que esperar su turno.
          </p>
        )}
        {narrErrores.length > 0 && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">
            Narración con errores: {narrErrores.map((e) => e.error).join('; ')}
          </p>
        )}
        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      <section className="panel flex min-h-0 flex-1 flex-col overflow-hidden" aria-label="clips del proyecto">
        <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Clips · {label}</span>
          <div className="flex items-center gap-1.5">
            {guided && (
              <Button size="xs" variant="accent" onClick={() => setAssistantOpen(true)}
                title="Escribe el script del clip a partir de un formulario">
                <Wand2 className="h-3.5 w-3.5" /> Asistente
              </Button>
            )}
            <Button size="xs" variant="primary" onClick={() => setAddClipOpen(true)}>
              <Plus className="h-3.5 w-3.5" /> Añadir clip
            </Button>
          </div>
        </div>
        <div className="min-h-0 flex-1 overflow-auto">
          {clips.length === 0 ? (
            <p className="p-4 text-[13px] text-muted">Sin clips todavía. Añade el primero para empezar el curso.</p>
          ) : (
            clips.map((clip, i) => (
              <ClipCard key={clip.id} clip={clip} index={i} total={clips.length}
                prevClip={i > 0 ? clips[i - 1] : null} jobs={jobs}
                onFieldChange={onFieldChange} onFieldBlur={onFieldBlur}
                onMove={move} onDelete={removeClip} onRender={renderClip}
                onOpenInStudio={openInStudio}
                projectId={project.id} narr={narrByClip[clip.id]}
                narrando={narrRun?.current?.clip_id === clip.id}
                narrBusy={Boolean(run)} narrEnabled={Boolean(narracion?.enabled)}
                onVerGuion={() => setGuionClip(clip)}
                onNarrar={() => generarNarracion({ clips: [clip.id], force: true })} />
            ))
          )}
        </div>
      </section>

      <StyleDialog open={styleOpen} onOpenChange={setStyleOpen} project={project}
        onSaved={(styleBlock, updatedAt) => setProject((p) => ({ ...p, style_block: styleBlock, updated_at: updatedAt }))} />
      <AddClipDialog open={addClipOpen} onOpenChange={setAddClipOpen} projectId={project.id}
        onCreated={() => { setAddClipOpen(false); load() }} />
      <GuionDialog projectId={project.id} clip={guionClip}
        onOpenChange={(o) => !o && setGuionClip(null)} />
      {guided && (
        <ClipAssistant open={assistantOpen} onOpenChange={setAssistantOpen}
          project={project} aiEnabled={aiEnabled}
          onCreated={() => { setAssistantOpen(false); load() }} />
      )}
    </main>
  )
}

const STAT_TONE = { ok: 'text-ok', warn: 'text-warn', muted: 'text-ink' }

function Stat({ label, value, detail, tone }) {
  return (
    <div className="rounded-lg border border-line bg-surface-2 px-3 py-2">
      <div className="eyebrow">{label}</div>
      <div className={cn('mt-0.5 font-mono text-[19px] font-semibold leading-none tabular-nums', STAT_TONE[tone] || 'text-ink')}>
        {value}
      </div>
      <div className="mt-1 text-[11.5px] text-muted">{detail}</div>
    </div>
  )
}

// Duracion del clip con el semaforo del formato (28-45 s).
function DurationBadge({ s }) {
  if (s == null) return null
  const fuera = s < DURACION_MIN || s > DURACION_MAX
  return (
    <span className={cn('rounded-md border px-1.5 py-0.5 font-mono text-[11px] tabular-nums',
      fuera ? 'border-warn/40 text-warn' : 'border-line text-muted')}
      title={fuera
        ? `fuera del rango del formato (${DURACION_MIN}-${DURACION_MAX} s)`
        : `dentro del rango del formato (${DURACION_MIN}-${DURACION_MAX} s)`}>
      {fmtDur(s)}
    </span>
  )
}

function ClipCard({ clip, index, total, prevClip, jobs, onFieldChange, onFieldBlur, onMove, onDelete, onRender, onOpenInStudio, projectId, narr, narrando, narrBusy, narrEnabled, onNarrar, onVerGuion }) {
  const activeJob = activeJobFor(jobs, clip.id)
  const renderJob = clip.job_id ? jobs.find((j) => j.id === clip.job_id) : null
  const meta = activeJob ? STATUS_META[activeJob.status] : (STATUS_META[clip.status] || STATUS_META.no_render)
  const canRender = !activeJob && Boolean(clip.scene?.trim())
  const narrMeta = narr ? (NARR_META[narr.estado] || NARR_META.sin_narracion) : null

  return (
    <article className="flex flex-col gap-2.5 border-b border-line p-3.5 last:border-b-0 sm:flex-row">
      <div className="relative aspect-video w-full shrink-0 overflow-hidden rounded-md border border-line bg-canvas sm:w-40">
        {renderJob?.has_thumb ? (
          <img src={thumbUrl(renderJob.id)} alt={`miniatura de ${clip.title}`} loading="lazy"
            className="h-full w-full object-cover" />
        ) : (
          <span className="grid h-full place-items-center text-faint"><Film className="h-6 w-6" /></span>
        )}
      </div>

      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-[11px] text-faint">#{index + 1}</span>
          <Input value={clip.title}
            onChange={(e) => onFieldChange(clip.id, 'title', e.target.value)}
            onBlur={() => onFieldBlur(clip.id, 'title')}
            aria-label="título del clip"
            className="h-7 max-w-xs px-2 text-[13px] font-semibold" />
          <span className={cn('flex items-center gap-1.5 rounded-md border border-line px-2 py-0.5 font-mono text-[11px] uppercase tracking-wide', meta.text)}>
            <span className={cn('h-1.5 w-1.5 rounded-full', meta.dot)} /> {meta.label}
          </span>
          <DurationBadge s={narr?.video_s} />
        </div>

        <label className="flex items-center gap-2 text-[12px] text-muted">
          escena
          <Input value={clip.scene || ''}
            onChange={(e) => onFieldChange(clip.id, 'scene', e.target.value)}
            onBlur={() => onFieldBlur(clip.id, 'scene')}
            placeholder="NombreDeEscena"
            className="h-7 max-w-[220px] px-2 font-mono text-[12px]" />
        </label>

        <details className="rounded-md border border-line/60 bg-canvas/40">
          <summary className="cursor-pointer select-none px-2.5 py-1.5 text-[11.5px] text-muted">
            Continuidad
          </summary>
          <div className="flex flex-col gap-2 border-t border-line/60 px-2.5 py-2 text-[12.5px]">
            <p className="text-muted">
              El clip anterior termina: {prevClip ? (prevClip.final_state?.trim() || 'sin nota') : '— (primer clip)'}
            </p>
            <label className="flex flex-col gap-1">
              <span className="eyebrow">Este clip termina en…</span>
              <textarea value={clip.final_state || ''} rows={2}
                onChange={(e) => onFieldChange(clip.id, 'final_state', e.target.value)}
                onBlur={() => onFieldBlur(clip.id, 'final_state')}
                className={textareaCls} />
            </label>
            <label className="flex flex-col gap-1">
              <span className="eyebrow">Notas</span>
              <textarea value={clip.notes || ''} rows={2}
                onChange={(e) => onFieldChange(clip.id, 'notes', e.target.value)}
                onBlur={() => onFieldBlur(clip.id, 'notes')}
                className={textareaCls} />
            </label>
          </div>
        </details>

        <div className="mt-1 flex flex-wrap items-center gap-1.5">
          <Button size="xs" variant="default" onClick={() => onOpenInStudio(clip)}>
            <Pencil className="h-3.5 w-3.5" /> Editar en Estudio
          </Button>
          <Button size="xs" variant="accent" onClick={() => onRender(clip.id)} disabled={!canRender}
            title={activeJob ? 'ya hay un render en curso para este clip' : (!clip.scene?.trim() ? 'asigna una escena primero' : undefined)}>
            Render
          </Button>
          <Button size="xs" variant="ghost" onClick={() => onMove(clip.id, clip.position - 1)}
            disabled={index === 0} aria-label="mover arriba">
            <ChevronUp className="h-3.5 w-3.5" />
          </Button>
          <Button size="xs" variant="ghost" onClick={() => onMove(clip.id, clip.position + 1)}
            disabled={index === total - 1} aria-label="mover abajo">
            <ChevronDown className="h-3.5 w-3.5" />
          </Button>
          <span className="ml-auto"><DeleteButton onDelete={() => onDelete(clip.id)} /></span>
        </div>

        {/* La fila de narracion se muestra SIEMPRE que el backend sepa algo del
            clip (antes solo aparecia con audio ya generado, asi que no habia
            forma de ver desde aqui que faltaba narrar). */}
        {narr && (
          <div className="mt-1 flex flex-wrap items-center gap-2 rounded-md border border-line/60 bg-canvas/40 px-2.5 py-1.5">
            <Mic className="h-3.5 w-3.5 shrink-0 text-accent" />
            {narrando ? (
              <span className="text-[12px] text-cyan">narrando…</span>
            ) : (
              <>
                <span className={cn('font-mono text-[11px] uppercase tracking-wide', narrMeta.text)}>
                  {narrMeta.label}
                </span>
                {narr.has_audio && (
                  <audio controls preload="none" src={narracionAudioUrl(projectId, clip.id)}
                    aria-label={`narración de ${clip.title}`} className="h-8 min-w-0 max-w-[280px] flex-1" />
                )}
                {narr.audio_s != null && (
                  <span className="font-mono text-[11px] text-muted">
                    {narr.audio_s} s{narr.voz ? ` · ${narr.voz}` : ''}
                  </span>
                )}
                {narr.aviso_largo && (
                  <span className="text-[11px] text-warn"
                    title="mux.sh la acelera con atempo al montar; no se corta">
                    ⚠ más larga que el video
                  </span>
                )}
                {narr.has_texto && (
                  <Button size="xs" variant="ghost" onClick={onVerGuion} title="ver el texto del guion">
                    <FileText className="h-3.5 w-3.5" /> Guion
                  </Button>
                )}
                <Button size="xs" variant="ghost" onClick={onNarrar} disabled={narrBusy || !narrEnabled}
                  aria-label="regenerar narración"
                  title={narrEnabled ? 'regenerar la narración de este clip' : 'requiere el asistente IA (Vertex)'}>
                  <RefreshCw className="h-3.5 w-3.5" />
                </Button>
              </>
            )}
          </div>
        )}
      </div>
    </article>
  )
}

// Lector del guion generado por Vertex: el endpoint existia desde el primer
// dia y no habia ninguna forma de leer el texto sin bajarse el zip del curso.
function GuionDialog({ projectId, clip, onOpenChange }) {
  const [texto, setTexto] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!clip) return
    setTexto(null); setError('')
    let alive = true
    api.getNarracionTexto(projectId, clip.id)
      .then((d) => { if (alive) setTexto(d) })
      .catch((err) => { if (alive) setError(err.message) })
    return () => { alive = false }
  }, [projectId, clip])

  return (
    <Dialog open={Boolean(clip)} onOpenChange={onOpenChange}>
      {clip && (
        <DialogContent className="p-0">
          <div className="border-b border-line px-4 py-3 pr-12">
            <DialogTitle className="truncate font-display text-[15px] text-ink">
              Guion · {clip.title}
            </DialogTitle>
          </div>
          <div className="max-h-[70vh] overflow-y-auto p-4">
            {error ? (
              <p role="alert" className="text-[13px] text-warn">{error}</p>
            ) : texto == null ? (
              <p className="text-[13px] text-muted">Cargando guion…</p>
            ) : (
              <p className="whitespace-pre-wrap text-[13.5px] leading-relaxed text-ink">
                {texto.txt || texto.md || 'Guion vacío.'}
              </p>
            )}
          </div>
        </DialogContent>
      )}
    </Dialog>
  )
}

function StyleDialog({ open, onOpenChange, project, onSaved }) {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) { setValue(project.style_block || ''); setError('') }
  }, [open, project.style_block])

  const submit = async (e) => {
    e.preventDefault()
    if (busy) return
    setBusy(true)
    setError('')
    try {
      const updated = await api.patchProject(project.id, { style_block: value })
      onSaved(updated.style_block, updated.updated_at)
      onOpenChange(false)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Estilo compartido del proyecto</DialogTitle>
            </div>
            <div className="flex flex-col gap-2 overflow-y-auto p-4">
              <p className="text-[12.5px] text-muted">
                Este código se antepone al script de cada clip antes de renderizar
                (imports, colores, helpers de continuidad…). Cambiarlo marca los
                clips ya renderizados como desactualizados.
              </p>
              <textarea value={value} onChange={(e) => setValue(e.target.value)} rows={14}
                spellCheck={false} className={cn(textareaCls, 'font-mono')} />
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy}>Guardar</Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}

function AddClipDialog({ open, onOpenChange, projectId, onCreated }) {
  const [title, setTitle] = useState('')
  const [scene, setScene] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) { setTitle(''); setScene(''); setError('') }
  }, [open])

  const submit = async (e) => {
    e.preventDefault()
    if (!title.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      await api.createClip(projectId, { title: title.trim(), scene: scene.trim() })
      onCreated()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Añadir clip</DialogTitle>
            </div>
            <div className="flex flex-col gap-3 p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Título</span>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} autoFocus required maxLength={200} />
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Escena (opcional)</span>
                <Input value={scene} onChange={(e) => setScene(e.target.value)} placeholder="NombreDeEscena"
                  className="font-mono" />
              </label>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy || !title.trim()}>Añadir</Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}
