// Renders — el archivo de todo lo que ha salido de la cola.
//
// Antes se llamaba "Biblioteca", nombre que chocaba con la biblioteca de
// contenido de Aprender, y partia la misma lista en dos bloques: una rejilla
// de videos arriba y una lista de "fallidos / cancelados" abajo. Son el mismo
// objeto (un job) en distinto estado, asi que ahora es UNA rejilla con filtro
// de estado. Y como casi todo render es el clip de un curso, cada tarjeta dice
// de que curso es y lleva de vuelta a el (esa es la union real con Proyectos,
// mejor que fusionar dos vistas con tareas distintas).

import { useEffect, useMemo, useState } from 'react'
import { Play, Download, FolderPlus, Search, ArrowUpRight } from 'lucide-react'
import { api, thumbUrl, videoUrl } from './api.js'
import { refreshCatalogo, useCatalogo } from './catalogo.js'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select.jsx'
import DeleteButton from './components/DeleteButton.jsx'
import { cn } from '@/lib/utils'

const MB = 1024 ** 2

function fmtSize(bytes) {
  if (bytes == null) return '—'
  if (bytes >= 1024 * MB) return `${(bytes / (1024 * MB)).toFixed(2)} GB`
  if (bytes >= MB) return `${(bytes / MB).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}

function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

function duration(job) {
  if (!job.started_at || !job.finished_at) return null
  return `${(job.finished_at - job.started_at).toFixed(0)}s`
}

const QUALITY_LABEL = { ql: '480p', qm: '720p', qh: '1080p' }

const STATE_META = {
  done: { label: 'listo', dot: 'bg-ok', text: 'text-ok' },
  error: { label: 'error', dot: 'bg-err', text: 'text-err' },
  timeout: { label: 'timeout', dot: 'bg-err', text: 'text-err' },
  cancelled: { label: 'cancelado', dot: 'bg-muted', text: 'text-muted' },
}

const FILTERS = [
  { id: 'listos', label: 'Con video' },
  { id: 'fallidos', label: 'Fallidos' },
  { id: 'todos', label: 'Todos' },
]

// El listado sube a 500 jobs (JOBS_LIST_LIMIT) y con ~60 cursos en catalogo
// son cientos de tarjetas: sin buscador ni orden es inservible.
const SORTS = [
  { id: 'recientes', label: 'Recientes' },
  { id: 'antiguos', label: 'Antiguos' },
  { id: 'grandes', label: 'Más pesados' },
  { id: 'nombre', label: 'Nombre' },
]

/** Medidor de cuota compacto: vive aqui porque es aqui donde se libera
 *  espacio borrando videos. La version con historia esta en Admin → Recursos. */
function StorageBar({ storage }) {
  if (!storage) return null
  const pct = storage.quota_bytes ? (storage.used_bytes / storage.quota_bytes) * 100 : 0
  const tone = pct >= 92 ? 'bg-err' : pct >= 75 ? 'bg-warn' : 'bg-cyan'
  return (
    <div className="flex min-w-0 flex-1 items-center gap-2.5" title="al superar la cuota no se aceptan nuevos renders">
      <span className="eyebrow shrink-0">Disco</span>
      <span className="h-1.5 w-[110px] shrink-0 overflow-hidden rounded-full border border-line bg-canvas"
        role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}
        aria-label="uso de disco de renders">
        <span className={cn('block h-full rounded-full transition-[width] duration-500', tone)}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </span>
      <span className="truncate font-mono text-[11px] text-muted">
        {fmtSize(storage.used_bytes)} / {fmtSize(storage.quota_bytes)}
      </span>
    </div>
  )
}

// Dialog "Añadir a proyecto…": carga los proyectos existentes al abrir y
// crea un clip a partir del job (from_job_id). El backend solo "adopta" el
// video (lo enlaza como ya renderizado) si la calidad coincide y el proyecto
// no tiene estilo compuesto que difiera del script del job; en cualquier
// caso el clip queda creado con el script/escena del render.
function AddToProjectDialog({ job, onOpenChange, onOpenProject }) {
  const catalogo = useCatalogo()
  const projects = catalogo.loaded ? catalogo.list : null
  const [pid, setPid] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [createdIn, setCreatedIn] = useState(null)

  // Abrir el dialogo con otro render lo reinicia. Ojo: esto NO puede depender
  // de `projects` — crear el clip refresca el catalogo, y con esa dependencia
  // el efecto borraria el "Clip creado" justo despues de mostrarlo.
  useEffect(() => {
    if (!job) return
    setPid(''); setError(''); setCreatedIn(null)
  }, [job])

  useEffect(() => {
    if (!pid && projects?.length) setPid(projects[0].id)
  }, [pid, projects])

  const submit = async (e) => {
    e.preventDefault()
    if (!pid || busy) return
    setBusy(true)
    setError('')
    try {
      await api.createClip(pid, { title: job.scene, from_job_id: job.id })
      // El curso acaba de ganar un clip: el indice compartido (y con el los
      // contadores de Proyectos) tiene que enterarse.
      refreshCatalogo()
      setCreatedIn(pid)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={!!job} onOpenChange={onOpenChange}>
      {job && (
        <DialogContent className="w-[min(420px,94vw)] p-0">
          <div className="border-b border-line px-4 py-3 pr-12">
            <DialogTitle className="font-display text-[15px] text-ink">Añadir a proyecto…</DialogTitle>
          </div>
          {createdIn ? (
            <div className="flex flex-col items-start gap-3 p-4">
              <p className="text-[13px] text-ok">Clip creado a partir de «{job.scene}».</p>
              <Button size="sm" variant="default"
                onClick={() => { onOpenChange(false); onOpenProject(createdIn) }}>
                Ver proyecto <ArrowUpRight className="h-3.5 w-3.5" />
              </Button>
            </div>
          ) : (
            <form onSubmit={submit} className="flex flex-col gap-3 p-4">
              <p className="text-[12.5px] text-muted">
                Crea un clip a partir de «{job.scene}» ({QUALITY_LABEL[job.quality] || job.quality})
                en el proyecto elegido. Si la calidad no coincide con la del
                proyecto, el clip se crea igual pero queda sin render.
              </p>
              {projects == null ? (
                <p className="text-[13px] text-muted">Cargando proyectos…</p>
              ) : projects.length === 0 ? (
                <p className="text-[13px] text-muted">
                  Sin proyectos todavía. Crea uno primero en la pestaña Proyectos.
                </p>
              ) : (
                <label className="flex flex-col gap-1">
                  <span className="eyebrow">Proyecto</span>
                  <Select value={pid} onValueChange={setPid}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {projects.map((p) => <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </label>
              )}
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
              <div className="flex justify-end gap-2">
                <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
                <Button type="submit" variant="primary" disabled={busy || !pid || !projects?.length}>
                  Añadir
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      )}
    </Dialog>
  )
}

export default function Renders({ jobs, storage, onJobsChanged, onOpenProject }) {
  const [playing, setPlaying] = useState(null)
  const [addingToProject, setAddingToProject] = useState(null)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [sort, setSort] = useState('recientes')
  const [filter, setFilter] = useState('listos')
  // Casi todos los renders son clips de un curso y su escena se llama
  // "Clip1".."Clip8": sin el nombre del proyecto la rejilla son cientos de
  // tarjetas indistinguibles. El indice se comparte con el resto de la app
  // (`catalogo.js`), asi que entrar aqui ya no lo vuelve a bajar.
  const catalogo = useCatalogo()
  const projectNames = useMemo(
    () => Object.fromEntries(catalogo.list.map((p) => [p.id, p.name])), [catalogo.list])

  const terminados = useMemo(
    () => jobs.filter((j) => ['done', 'error', 'timeout', 'cancelled'].includes(j.status)),
    [jobs])
  const conVideo = terminados.filter((j) => j.status === 'done')
  const fallidos = terminados.filter((j) => j.status !== 'done')

  const q = query.trim().toLowerCase()
  const visible = useMemo(() => {
    const base = filter === 'listos' ? conVideo : filter === 'fallidos' ? fallidos : terminados
    const texto = (j) => `${j.scene} ${projectNames[j.project_id] || ''}`.toLowerCase()
    const list = q ? base.filter((j) => texto(j).includes(q)) : [...base]
    const cmp = {
      recientes: (a, b) => b.created_at - a.created_at,
      antiguos: (a, b) => a.created_at - b.created_at,
      grandes: (a, b) => (b.size_bytes || 0) - (a.size_bytes || 0),
      nombre: (a, b) => a.scene.localeCompare(b.scene, 'es'),
    }[sort]
    return list.sort(cmp)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobs, q, sort, filter, projectNames])

  const remove = async (id) => {
    setError('')
    try {
      await api.deleteJob(id)
      if (playing?.id === id) setPlaying(null)
      onJobsChanged()
    } catch (err) {
      setError(err.message)
    }
  }

  const countOf = (id) => (id === 'listos' ? conVideo.length : id === 'fallidos' ? fallidos.length : terminados.length)

  return (
    <main data-view="renders" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="renders">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Renders</span>
          <div className="flex flex-wrap items-center gap-2">
            {/* Filtro de estado: antes eran dos bloques distintos en la pagina
                (rejilla de videos y lista de fallidos) para el mismo objeto. */}
            <div role="radiogroup" aria-label="estado" className="flex rounded-md border border-line bg-canvas p-0.5">
              {FILTERS.map((f) => (
                <button key={f.id} type="button" role="radio" aria-checked={filter === f.id}
                  onClick={() => setFilter(f.id)}
                  className={cn(
                    'rounded-[5px] px-2.5 py-1 text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                    filter === f.id ? 'bg-surface-2 text-accent shadow-sm' : 'text-muted hover:text-ink',
                  )}>
                  {f.label} <span className="font-mono text-[10px] text-faint">{countOf(f.id)}</span>
                </button>
              ))}
            </div>
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-faint" />
              <Input type="search" value={query} onChange={(e) => setQuery(e.target.value)}
                placeholder="Buscar escena o curso…" aria-label="buscar renders"
                className="h-8 w-[200px] pl-8 text-[13px]" />
            </div>
            <Select value={sort} onValueChange={setSort}>
              <SelectTrigger className="h-8 w-[140px]" aria-label="ordenar renders"><SelectValue /></SelectTrigger>
              <SelectContent>
                {SORTS.map((s) => <SelectItem key={s.id} value={s.id}>{s.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-line px-3 py-2">
          <StorageBar storage={storage} />
          <span className="font-mono text-[11px] text-faint">
            {visible.length}{q || filter !== 'todos' ? ` de ${terminados.length}` : ''} render{terminados.length === 1 ? '' : 's'}
          </span>
        </div>

        {visible.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">
            {q ? 'Ningún render coincide con la búsqueda.'
              : filter === 'fallidos' ? 'Ningún render ha fallado. '
                : 'Sin renders todavía. Los que salgan de la cola aparecen aquí.'}
          </p>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-3.5 p-4">
            {visible.map((j) => (
              <RenderCard key={j.id} job={j} projectName={projectNames[j.project_id]}
                onPlay={() => setPlaying(j)} onAddToProject={() => setAddingToProject(j)}
                onOpenProject={onOpenProject} onDelete={() => remove(j.id)} />
            ))}
          </div>
        )}

        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      <AddToProjectDialog job={addingToProject} onOpenProject={onOpenProject}
        onOpenChange={(o) => !o && setAddingToProject(null)} />

      <Dialog open={!!playing} onOpenChange={(o) => !o && setPlaying(null)}>
        {playing && (
          <DialogContent className="p-0">
            <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2 pr-12">
              <DialogTitle className="truncate font-mono text-[13px] text-ink">
                {playing.scene} <span className="text-faint">· {playing.id.slice(0, 8)}</span>
              </DialogTitle>
            </div>
            <video className="block max-h-[78vh] w-full bg-black" controls autoPlay src={videoUrl(playing.id)} />
          </DialogContent>
        )}
      </Dialog>
    </main>
  )
}

function RenderCard({ job, projectName, onPlay, onAddToProject, onOpenProject, onDelete }) {
  const m = STATE_META[job.status] || STATE_META.error
  const hasVideo = job.status === 'done'
  return (
    <article className="group flex flex-col overflow-hidden rounded-lg border border-line bg-surface-2 transition-colors hover:border-line-strong">
      {hasVideo ? (
        <button onClick={onPlay} aria-label={`ver ${job.scene}`}
          className="relative block aspect-video w-full border-b border-line bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
          {job.has_thumb
            ? <img src={thumbUrl(job.id)} alt={`miniatura de ${job.scene}`} loading="lazy"
                className="h-full w-full object-cover" />
            : <span className="grid h-full place-items-center text-faint"><Play className="h-7 w-7" /></span>}
          <span className="absolute inset-0 grid place-items-center bg-canvas/45 text-accent opacity-0 transition-opacity group-hover:opacity-100">
            <Play className="h-9 w-9" fill="currentColor" />
          </span>
        </button>
      ) : (
        <div className="grid aspect-video w-full place-items-center border-b border-line bg-canvas px-3 text-center">
          <span className={cn('font-mono text-[11px] uppercase tracking-wide', m.text)}>{m.label}</span>
        </div>
      )}
      <div className="flex flex-1 flex-col gap-1.5 p-3">
        {projectName && (
          <button onClick={() => onOpenProject(job.project_id)}
            title={`ir a ${projectName}`}
            className="flex items-center gap-1 truncate text-left text-[11.5px] text-accent hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
            <span className="truncate">{projectName}</span>
            <ArrowUpRight className="h-3 w-3 shrink-0" />
          </button>
        )}
        <h3 className="truncate font-mono text-[13px] font-semibold text-ink" title={job.scene}>{job.scene}</h3>
        <p className="text-[11.5px] text-muted">
          {fmtDate(job.created_at)} · {duration(job) || '—'} · {QUALITY_LABEL[job.quality] || job.quality}
          {hasVideo && <> · {fmtSize(job.size_bytes)}</>}
        </p>
        {/* El motivo del fallo vivia solo en el chip del Estudio. */}
        {job.error && (
          <p className="break-words font-mono text-[11px] leading-snug text-err/90" title={job.error}>
            ✕ {job.error}
          </p>
        )}
        <div className="mt-auto flex flex-wrap gap-1.5 pt-1.5">
          {hasVideo && (
            <>
              <Button size="xs" variant="default" onClick={onPlay}>Ver</Button>
              <Button size="xs" variant="default" asChild>
                <a href={videoUrl(job.id)} download={`${job.scene}.mp4`}>
                  <Download className="h-3.5 w-3.5" /> Descargar
                </a>
              </Button>
              <Button size="xs" variant="default" onClick={onAddToProject}>
                <FolderPlus className="h-3.5 w-3.5" /> A un proyecto…
              </Button>
            </>
          )}
          <span className={hasVideo ? '' : 'ml-auto'}>
            <DeleteButton onDelete={onDelete}
              confirmText={job.clip_id
                ? 'Es el render de un clip; el clip quedará sin video. ¿Confirmar?'
                : undefined} />
          </span>
        </div>
      </div>
    </article>
  )
}
