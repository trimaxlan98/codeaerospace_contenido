// Biblioteca: videos renderizados (grid de tarjetas) + gestión de disco.

import { useEffect, useMemo, useState } from 'react'
import { Play, Download, FolderPlus, Search } from 'lucide-react'
import { api, thumbUrl, videoUrl } from './api.js'
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
const FAIL_META = {
  error: { label: 'error', dot: 'bg-err', text: 'text-err' },
  timeout: { label: 'timeout', dot: 'bg-err', text: 'text-err' },
  cancelled: { label: 'cancelado', dot: 'bg-muted', text: 'text-muted' },
}

function StorageBar({ storage }) {
  if (!storage) return null
  const pct = storage.quota_bytes ? (storage.used_bytes / storage.quota_bytes) * 100 : 0
  const tone = pct >= 92 ? 'bg-err' : pct >= 75 ? 'bg-warn' : 'bg-cyan'
  return (
    <div className="max-w-xl">
      <div className="mb-1.5 flex items-center justify-between">
        <span className="eyebrow">Almacenamiento · render_jobs/</span>
        <span className="font-mono text-xs tabular-nums text-ink">{pct.toFixed(1)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full border border-line bg-canvas"
        role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}
        aria-label="uso de disco de renders">
        <div className={cn('h-full rounded-full transition-[width] duration-500', tone)}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <p className="mt-1.5 text-[11.5px] text-muted">
        {fmtSize(storage.used_bytes)} de {fmtSize(storage.quota_bytes)} · al superar la cuota
        no se aceptan nuevos renders
      </p>
    </div>
  )
}

// Dialog "Añadir a proyecto…": carga los proyectos existentes al abrir y
// crea un clip a partir del job (from_job_id). El backend solo "adopta" el
// video (lo enlaza como ya renderizado) si la calidad coincide y el proyecto
// no tiene estilo compuesto que difiera del script del job; en cualquier
// caso el clip queda creado con el script/escena del render.
function AddToProjectDialog({ job, onOpenChange }) {
  const [projects, setProjects] = useState(null)
  const [pid, setPid] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [createdIn, setCreatedIn] = useState(null) // id del proyecto tras crear

  useEffect(() => {
    if (!job) return
    setProjects(null); setPid(''); setError(''); setCreatedIn(null)
    api.listProjects().then((d) => {
      setProjects(d.projects)
      if (d.projects.length) setPid(d.projects[0].id)
    }).catch((err) => setError(err.message))
  }, [job])

  const submit = async (e) => {
    e.preventDefault()
    if (!pid || busy) return
    setBusy(true)
    setError('')
    try {
      await api.createClip(pid, { title: job.scene, from_job_id: job.id })
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
              <a href={`#/proyectos/${createdIn}`}
                onClick={() => onOpenChange(false)}
                className="text-[13px] text-cyan underline underline-offset-2 hover:text-ink">
                Ver proyecto →
              </a>
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

// El listado sube a 500 jobs (JOBS_LIST_LIMIT) y con ~60 cursos en catalogo
// la rejilla son cientos de tarjetas: sin buscador ni orden es inservible.
const SORTS = [
  { id: 'recientes', label: 'Recientes' },
  { id: 'antiguos', label: 'Antiguos' },
  { id: 'grandes', label: 'Más pesados' },
  { id: 'nombre', label: 'Nombre' },
]

export default function Library({ jobs, storage, onJobsChanged }) {
  const [playing, setPlaying] = useState(null) // job en el visor
  const [addingToProject, setAddingToProject] = useState(null) // job a enlazar
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [sort, setSort] = useState('recientes')
  const [projectNames, setProjectNames] = useState({})

  // Casi todos los renders son clips de un curso y su escena se llama
  // "Clip1".."Clip8": sin el nombre del proyecto la rejilla son cientos de
  // tarjetas indistinguibles. Una sola consulta al montar basta.
  useEffect(() => {
    api.listProjects()
      .then((d) => setProjectNames(Object.fromEntries(d.projects.map((p) => [p.id, p.name]))))
      .catch(() => { /* sin nombres: la tarjeta cae al nombre de escena */ })
  }, [])

  const allVideos = jobs.filter((j) => j.status === 'done')
  const failed = jobs.filter((j) => ['error', 'timeout', 'cancelled'].includes(j.status))

  const q = query.trim().toLowerCase()
  const videos = useMemo(() => {
    const texto = (j) => `${j.scene} ${projectNames[j.project_id] || ''}`.toLowerCase()
    const list = q ? allVideos.filter((j) => texto(j).includes(q)) : [...allVideos]
    const cmp = {
      recientes: (a, b) => b.created_at - a.created_at,
      antiguos: (a, b) => a.created_at - b.created_at,
      grandes: (a, b) => (b.size_bytes || 0) - (a.size_bytes || 0),
      nombre: (a, b) => a.scene.localeCompare(b.scene, 'es'),
    }[sort]
    return list.sort(cmp)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobs, q, sort, projectNames])

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

  return (
    <main className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      {/* shrink-0: sin el, las secciones se comprimen para caber en el
          viewport y su contenido se pinta encima de la siguiente. */}
      <section className="panel shrink-0" aria-label="uso de disco">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Biblioteca</span>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-[11px] text-faint">
              {q ? `${videos.length}/${allVideos.length}` : videos.length} video{allVideos.length === 1 ? '' : 's'}
            </span>
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-faint" />
              <Input type="search" value={query} onChange={(e) => setQuery(e.target.value)}
                placeholder="Buscar escena…" aria-label="buscar videos"
                className="h-8 w-[180px] pl-8 text-[13px]" />
            </div>
            <Select value={sort} onValueChange={setSort}>
              <SelectTrigger className="h-8 w-[140px]" aria-label="ordenar videos"><SelectValue /></SelectTrigger>
              <SelectContent>
                {SORTS.map((s) => <SelectItem key={s.id} value={s.id}>{s.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="p-4">
          <StorageBar storage={storage} />
        </div>
        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      <section className="panel shrink-0" aria-label="videos renderizados">
        {videos.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">
            {q ? 'Ningún video coincide con la búsqueda.'
              : 'Sin videos todavía. Los renders exitosos aparecen aquí.'}
          </p>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-3.5 p-4">
            {videos.map((j) => (
              <article key={j.id} className="group flex flex-col overflow-hidden rounded-lg border border-line bg-surface-2 transition-colors hover:border-line-strong">
                <button onClick={() => setPlaying(j)} aria-label={`ver ${j.scene}`}
                  className="relative block aspect-video w-full border-b border-line bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                  {j.has_thumb
                    ? <img src={thumbUrl(j.id)} alt={`miniatura de ${j.scene}`} loading="lazy"
                        className="h-full w-full object-cover" />
                    : <span className="grid h-full place-items-center text-faint"><Play className="h-7 w-7" /></span>}
                  <span className="absolute inset-0 grid place-items-center bg-canvas/45 text-accent opacity-0 transition-opacity group-hover:opacity-100">
                    <Play className="h-9 w-9" fill="currentColor" />
                  </span>
                </button>
                <div className="flex flex-col gap-1.5 p-3">
                  {projectNames[j.project_id] && (
                    <p className="truncate text-[11.5px] text-accent" title={projectNames[j.project_id]}>
                      {projectNames[j.project_id]}
                    </p>
                  )}
                  <h3 className="truncate font-mono text-[13px] font-semibold text-ink" title={j.scene}>{j.scene}</h3>
                  <p className="text-[11.5px] text-muted">
                    {fmtDate(j.created_at)} · {duration(j) || '—'} · {QUALITY_LABEL[j.quality] || j.quality} · {fmtSize(j.size_bytes)}
                  </p>
                  <div className="mt-1 flex flex-wrap gap-1.5">
                    <Button size="xs" variant="default" onClick={() => setPlaying(j)}>Ver</Button>
                    <Button size="xs" variant="default" asChild>
                      <a href={videoUrl(j.id)} download={`${j.scene}.mp4`}>
                        <Download className="h-3.5 w-3.5" /> Descargar
                      </a>
                    </Button>
                    <Button size="xs" variant="default" onClick={() => setAddingToProject(j)}>
                      <FolderPlus className="h-3.5 w-3.5" /> Añadir a proyecto…
                    </Button>
                    <DeleteButton onDelete={() => remove(j.id)}
                      confirmText={j.clip_id
                        ? 'Es el render de un clip; el clip quedará sin video. ¿Confirmar?'
                        : undefined} />
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {failed.length > 0 && (
        <section className="panel shrink-0" aria-label="historial de fallos">
          <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
            <span className="eyebrow">Fallidos / cancelados</span>
            <span className="font-mono text-[11px] text-faint">sin video · solo registro</span>
          </div>
          <ul className="divide-y divide-line/40">
            {failed.map((j) => {
              const m = FAIL_META[j.status] || FAIL_META.error
              return (
                <li key={j.id} className="flex flex-wrap items-center gap-x-3 gap-y-1 px-3 py-2">
                  <span className={cn('h-2 w-2 shrink-0 rounded-full', m.dot)} />
                  <span className="font-mono text-[13px] text-ink">{j.scene}</span>
                  {projectNames[j.project_id] && (
                    <span className="truncate text-[11.5px] text-accent">{projectNames[j.project_id]}</span>
                  )}
                  <span className="text-[11.5px] text-muted">{fmtDate(j.created_at)}</span>
                  <span className={cn('font-mono text-[11px] uppercase tracking-wide', m.text)}>{m.label}</span>
                  <span className="ml-auto"><DeleteButton onDelete={() => remove(j.id)} /></span>
                  {/* El motivo del fallo vivia solo en el chip del Estudio: aqui
                      se veia "error" y nada mas. */}
                  {j.error && (
                    <span className="w-full break-words font-mono text-[11.5px] text-err/90" title={j.error}>
                      ✕ {j.error}
                    </span>
                  )}
                </li>
              )
            })}
          </ul>
        </section>
      )}

      <AddToProjectDialog job={addingToProject}
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
