// Proyectos (cursos): agrupan clips ordenados con continuidad narrativa y
// estilo compartido. Lista de tarjetas + detalle con gestion de clips,
// render individual/masivo y exportacion del curso completo.

import { useCallback, useEffect, useRef, useState } from 'react'
import {
  ChevronDown, ChevronUp, Download, FileJson, FolderKanban, Film,
  Mic, Pencil, Plus, RefreshCw, Square,
} from 'lucide-react'
import { api, narracionAudioUrl, projectArchiveUrl, projectExportUrl, thumbUrl } from './api.js'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select.jsx'
import DeleteButton from './components/DeleteButton.jsx'
import { cn } from '@/lib/utils'

const QUALITY_LABEL = { ql: '480p', qm: '720p', qh: '1080p' }

const STATUS_META = {
  rendered: { label: 'renderizado', dot: 'bg-ok', text: 'text-ok' },
  stale: { label: 'desactualizado', dot: 'bg-warn', text: 'text-warn' },
  no_render: { label: 'sin render', dot: 'bg-muted', text: 'text-muted' },
  queued: { label: 'en cola', dot: 'bg-cyan', text: 'text-cyan' },
  running: { label: 'renderizando', dot: 'bg-cyan', text: 'text-cyan' },
}

function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

// Job en vuelo (queued/running) para un clip: hallazgo M-2 de la revision del
// backend — hay que evitar disparar un segundo render mientras el primero
// sigue en cola o corriendo, y reflejarlo en el badge de estado.
function activeJobFor(jobs, clipId) {
  return jobs.find((j) => j.clip_id === clipId && (j.status === 'queued' || j.status === 'running'))
}

// Clips stale/no_render que NO tienen ya un job en vuelo: hallazgo M-3 de la
// revision — sirve tanto para decidir si el boton masivo esta habilitado
// como para saber si hace falta evitar el endpoint global (que reencolaria
// un clip cuyo render sigue en curso, porque su rendered_hash aun no cambio).
function staleWithoutActiveJob(clips, jobs) {
  return clips.filter((c) => (c.status === 'stale' || c.status === 'no_render') && !activeJobFor(jobs, c.id))
}

const textareaCls = 'w-full resize-y rounded-md border border-line bg-canvas px-2.5 py-1.5 text-[12.5px] text-ink placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan'

export default function Projects({ jobs, onEditClip, routeId, onRoute }) {
  if (routeId) {
    return (
      <ProjectDetail key={routeId} projectId={routeId} jobs={jobs}
        onEditClip={onEditClip} onBack={() => onRoute(null)} />
    )
  }
  return <ProjectsList onOpen={(id) => onRoute(id)} />
}

// ── lista ────────────────────────────────────────────────────────────────

function ProjectsList({ onOpen }) {
  const [projects, setProjects] = useState(null)
  const [error, setError] = useState('')
  const [newOpen, setNewOpen] = useState(false)

  const load = useCallback(() => {
    setError('')
    api.listProjects().then((d) => setProjects(d.projects)).catch((err) => setError(err.message))
  }, [])

  useEffect(() => { load() }, [load])

  const remove = async (id) => {
    setError('')
    try {
      await api.deleteProject(id)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="proyectos">
        <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Proyectos</span>
          <Button size="sm" variant="primary" onClick={() => setNewOpen(true)}>
            <Plus className="h-3.5 w-3.5" /> Nuevo proyecto
          </Button>
        </div>

        {projects == null ? (
          <p className="p-4 text-[13px] text-muted">Cargando proyectos…</p>
        ) : projects.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">
            Sin proyectos todavía. Crea uno para agrupar clips en un curso con continuidad.
          </p>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-3.5 p-4">
            {projects.map((p) => (
              <ProjectCard key={p.id} project={p} onOpen={() => onOpen(p.id)} onDelete={() => remove(p.id)} />
            ))}
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

function ProjectCard({ project, onOpen, onDelete }) {
  return (
    <article className="group flex flex-col gap-2.5 overflow-hidden rounded-lg border border-line bg-surface-2 p-3.5 transition-colors hover:border-accent/50">
      <button onClick={onOpen}
        className="flex flex-col gap-1.5 rounded-md text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
        <div className="flex items-center gap-2">
          <FolderKanban className="h-4 w-4 shrink-0 text-accent" />
          <h3 className="truncate font-display text-[15px] font-semibold text-ink" title={project.name}>
            {project.name}
          </h3>
        </div>
        {project.description && (
          <p className="line-clamp-2 text-[12.5px] text-muted">{project.description}</p>
        )}
        <p className="text-[11.5px] text-muted">
          {project.clip_count} clip{project.clip_count === 1 ? '' : 's'} · {project.rendered_count} listo{project.rendered_count === 1 ? '' : 's'}
          {project.stale_count > 0 && (
            <span className="text-warn"> · {project.stale_count} desactualizado{project.stale_count === 1 ? '' : 's'}</span>
          )}
        </p>
        <p className="font-mono text-[11px] text-faint">
          {QUALITY_LABEL[project.quality] || project.quality} · {fmtDate(project.updated_at)}
        </p>
      </button>
      <div className="mt-auto flex justify-end">
        <DeleteButton onDelete={onDelete} />
      </div>
    </article>
  )
}

function NewProjectDialog({ open, onOpenChange, onCreated }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [quality, setQuality] = useState('qm')
  const [styleBlock, setStyleBlock] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) {
      setName(''); setDescription(''); setQuality('qm'); setStyleBlock(''); setError('')
    }
  }, [open])

  const submit = async (e) => {
    e.preventDefault()
    if (!name.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      const p = await api.createProject({
        name: name.trim(), description, quality, style_block: styleBlock,
      })
      onCreated(p)
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
              <DialogTitle className="font-display text-[15px] text-ink">Nuevo proyecto</DialogTitle>
            </div>
            <div className="flex flex-col gap-3 overflow-y-auto p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Nombre</span>
                <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus required maxLength={120} />
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
                  placeholder="Código Python que se antepone a cada clip (imports, colores, helpers…)"
                  className={cn(textareaCls, 'font-mono')} />
              </label>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy || !name.trim()}>Crear</Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}

// ── detalle ──────────────────────────────────────────────────────────────

function ProjectDetail({ projectId, jobs, onEditClip, onBack }) {
  const [project, setProject] = useState(null)
  const [narracion, setNarracion] = useState(null)
  const [error, setError] = useState('')
  const [styleOpen, setStyleOpen] = useState(false)
  const [addClipOpen, setAddClipOpen] = useState(false)
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

  // Mientras hay una narracion en curso se sondea el estado cada 3 s; el
  // resultado durable vive en estado.json del backend, esto es solo progreso.
  const narrRun = narracion?.run && !narracion.run.finished ? narracion.run : null
  useEffect(() => {
    if (!narrRun) return
    const t = setInterval(loadNarracion, 3000)
    return () => clearInterval(t)
  }, [narrRun != null, loadNarracion]) // eslint-disable-line react-hooks/exhaustive-deps

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
        // clip_public no devuelve status/stale recalculados (M-1): el hash de
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
      <main className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
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
  // Cuenta solo los stale/no_render sin job en vuelo (M-3): coherente con lo
  // que "Re-renderizar desactualizados" realmente va a encolar.
  const staleCount = staleWithoutActiveJob(clips, jobs).length
  const narrByClip = Object.fromEntries((narracion?.clips || []).map((c) => [c.clip_id, c]))
  const narrPending = (narracion?.clips || []).filter((c) => c.estado !== 'al_dia').length
  const narrErrores = (narracion?.run?.finished && narracion.run.errores) || []

  return (
    <main className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="cabecera del proyecto">
        <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
          <Button size="xs" variant="ghost" onClick={onBack}>← Proyectos</Button>
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
                disabled={!narracion?.enabled || narrPending === 0}
                title={!narracion?.enabled
                  ? 'requiere el asistente IA (Vertex) configurado'
                  : (narrPending === 0 ? 'la narración de todos los clips está al día' : undefined)}>
                <Mic className="h-3.5 w-3.5" /> Generar narración{narrPending > 0 ? ` (${narrPending})` : ''}
              </Button>
            )}
            <Button size="sm" variant="default" onClick={() => setStyleOpen(true)}>
              <Pencil className="h-3.5 w-3.5" /> Editar estilo
            </Button>
          </div>
        </div>

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
          <span className="eyebrow">Clips</span>
          <Button size="xs" variant="primary" onClick={() => setAddClipOpen(true)}>
            <Plus className="h-3.5 w-3.5" /> Añadir clip
          </Button>
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
                narrBusy={Boolean(narrRun)} narrEnabled={Boolean(narracion?.enabled)}
                onNarrar={() => generarNarracion({ clips: [clip.id], force: true })} />
            ))
          )}
        </div>
      </section>

      <StyleDialog open={styleOpen} onOpenChange={setStyleOpen} project={project}
        onSaved={(styleBlock, updatedAt) => setProject((p) => ({ ...p, style_block: styleBlock, updated_at: updatedAt }))} />
      <AddClipDialog open={addClipOpen} onOpenChange={setAddClipOpen} projectId={project.id}
        onCreated={() => { setAddClipOpen(false); load() }} />
    </main>
  )
}

function ClipCard({ clip, index, total, prevClip, jobs, onFieldChange, onFieldBlur, onMove, onDelete, onRender, onOpenInStudio, projectId, narr, narrando, narrBusy, narrEnabled, onNarrar }) {
  const activeJob = activeJobFor(jobs, clip.id)
  const renderJob = clip.job_id ? jobs.find((j) => j.id === clip.job_id) : null
  const meta = activeJob ? STATUS_META[activeJob.status] : (STATUS_META[clip.status] || STATUS_META.no_render)
  const canRender = !activeJob && Boolean(clip.scene?.trim())

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

        {(narr?.has_audio || narrando) && (
          <div className="mt-1 flex flex-wrap items-center gap-2 rounded-md border border-line/60 bg-canvas/40 px-2.5 py-1.5">
            <Mic className="h-3.5 w-3.5 shrink-0 text-accent" />
            {narrando ? (
              <span className="text-[12px] text-cyan">narrando…</span>
            ) : (
              <>
                <audio controls preload="none" src={narracionAudioUrl(projectId, clip.id)}
                  aria-label={`narración de ${clip.title}`} className="h-8 min-w-0 max-w-[300px] flex-1" />
                <span className="font-mono text-[11px] text-muted">
                  {narr.audio_s ? `${narr.audio_s} s · ` : ''}{narr.voz}
                </span>
                {narr.estado === 'desactualizada' && (
                  <span className="text-[11px] text-warn">desactualizada</span>
                )}
                {narr.aviso_largo && (
                  <span className="text-[11px] text-warn"
                    title="mux.sh la acelera con atempo al montar; no se corta">
                    ⚠ más larga que el video
                  </span>
                )}
                <Button size="xs" variant="ghost" onClick={onNarrar} disabled={narrBusy || !narrEnabled}
                  aria-label="regenerar narración" title="regenerar la narración de este clip">
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
