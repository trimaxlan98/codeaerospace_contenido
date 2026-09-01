import { useCallback, useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { Play, Sparkles, Wrench, Download, FileCode, RotateCcw, Trash2, X, Save, FolderKanban, LogOut, ArrowLeft } from 'lucide-react'
import { api, videoUrl } from './api.js'
import { cursoDeJob, useCatalogo } from './catalogo.js'
import Assistant from './Assistant.jsx'
import { Button } from './components/ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select.jsx'
import { cn } from '@/lib/utils'
import { useEditorTheme } from './themes.js'

const SAMPLE = `from manim import *


class Orbita(Scene):
    def construct(self):
        planeta = Circle(radius=0.5, color=BLUE, fill_opacity=1)
        orbita = Ellipse(width=6, height=3, color=GREY_B)
        satelite = Dot(color=YELLOW).move_to(orbita.point_from_proportion(0))
        self.play(FadeIn(planeta), Create(orbita))
        self.play(MoveAlongPath(satelite, orbita), run_time=4, rate_func=linear)
        self.wait()
`

const QUALITIES = [
  { id: 'ql', label: '480p', hint: 'borrador' },
  { id: 'qm', label: '720p', hint: 'media' },
  { id: 'qh', label: '1080p', hint: 'alta' },
]

const QUALITY_LABEL = Object.fromEntries(QUALITIES.map((q) => [q.id, q.label]))

// Persistencia local del area de trabajo: el script (y sus ajustes) deben
// sobrevivir a F5 y a cambios de vista. localStorage puede fallar (modo
// privado, cuota): nunca es fatal.
const LS = {
  script: 'ms_studio_script',
  scene: 'ms_studio_scene',
  quality: 'ms_studio_quality',
  timeout: 'ms_studio_timeout',
}

function lsGet(key) {
  try { return localStorage.getItem(key) } catch { return null }
}

function lsSet(key, value) {
  try { localStorage.setItem(key, value) } catch { /* no critico */ }
}

const STATUS_META = {
  queued: { label: 'en cola', dot: 'bg-cyan', text: 'text-cyan' },
  running: { label: 'renderizando', dot: 'bg-accent', text: 'text-accent' },
  done: { label: 'listo', dot: 'bg-ok', text: 'text-ok' },
  error: { label: 'error', dot: 'bg-err', text: 'text-err' },
  timeout: { label: 'timeout', dot: 'bg-err', text: 'text-err' },
  cancelled: { label: 'cancelado', dot: 'bg-muted', text: 'text-muted' },
  default: { label: '—', dot: 'bg-muted', text: 'text-muted' },
}

function fmtTime(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleTimeString('es', { hour12: false })
}

function duration(job) {
  if (!job.started_at) return null
  const end = job.finished_at || Date.now() / 1000
  return `${(end - job.started_at).toFixed(0)}s`
}

// Control segmentado (calidad). role=radiogroup para accesibilidad.
// disabled: se usa cuando el Estudio esta en contexto de clip — la calidad
// la fija el proyecto y no se puede cambiar desde aqui.
function Segmented({ options, value, onChange, ariaLabel, disabled }) {
  return (
    <div role="radiogroup" aria-label={ariaLabel} aria-disabled={disabled || undefined}
      className={cn('flex rounded-md border border-line bg-canvas p-0.5', disabled && 'opacity-60')}>
      {options.map((o) => {
        const on = value === o.id
        return (
          <button key={o.id} type="button" role="radio" aria-checked={on} title={o.hint}
            disabled={disabled}
            onClick={() => onChange(o.id)}
            className={cn(
              'rounded-[5px] px-2.5 py-1 font-mono text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
              on ? 'bg-surface-2 text-accent shadow-sm' : 'text-muted hover:text-ink',
              disabled && 'cursor-not-allowed',
            )}>
            {o.label}
          </button>
        )
      })}
    </div>
  )
}

// La identidad CO.DE Academy no es opcional ni configurable: el backend anexa
// el bloque de marca al final de TODO script antes de renderizar
// (`app/branding.py`, en el unico sitio donde se escribe scene.py), salvo que
// el script ya mencione `code_brand` — misma regla que `branding.ya_marcado`.
// Este distintivo solo lo cuenta: hasta ahora la garantia existia y no se veia
// por ninguna parte (encargo 11).
const MARCA_PROPIA = /code_brand/

function MarcaChip({ script }) {
  const propia = MARCA_PROPIA.test(script)
  return (
    <span
      className="hidden items-center gap-1.5 rounded-md border border-brand/35 px-2 py-0.5 font-mono text-[10.5px] uppercase tracking-wide text-brand sm:inline-flex"
      title={propia
        ? 'El script ya aplica la identidad CO.DE Academy por su cuenta (menciona code_brand): el servidor no añade nada.'
        : 'El servidor anexa la identidad CO.DE Academy al final del script antes de renderizar. No hace falta pedirlo y no se puede desactivar.'}
    >
      <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-brand" />
      marca {propia ? 'propia' : 'automática'}
    </span>
  )
}

// Accion secundaria dentro de una ficha (no dispara el onSelect del chip).
function ChipAction({ onClick, danger, title, children }) {
  return (
    <button type="button" title={title}
      onClick={(e) => { e.stopPropagation(); onClick() }}
      className={cn(
        'inline-flex w-fit items-center gap-1 rounded px-1.5 py-0.5 text-[11px] text-muted transition-colors',
        danger ? 'hover:bg-err/10 hover:text-err' : 'hover:bg-surface-2 hover:text-ink',
      )}>
      {children}
    </button>
  )
}

// Ficha de la tira de renders. Div interactivo (las acciones anidan dentro).
// queuePos: posicion 1-based entre los encolados (solo status=queued).
// curso: de que proyecto es el clip. Casi todo render del catalogo se llama
// `Clip3`, asi que sin esta linea la tira no permite distinguir un clip de
// otro entre ~300.
function JobChip({ job, curso, selected, onSelect, onCancel, onRetry, onDelete, queuePos }) {
  const m = STATUS_META[job.status] || STATUS_META.default
  const active = ['queued', 'running'].includes(job.status)
  const [arming, setArming] = useState(false)
  useEffect(() => {
    if (!arming) return
    const t = setTimeout(() => setArming(false), 3500)
    return () => clearTimeout(t)
  }, [arming])
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect() } }}
      className={cn(
        'flex w-[196px] shrink-0 cursor-pointer flex-col gap-1 rounded-lg border p-2.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
        selected ? 'border-accent/50 bg-surface-2' : 'border-line bg-surface hover:border-line-strong',
      )}
    >
      <div className="flex items-center gap-2">
        <span className={cn('h-2 w-2 shrink-0 rounded-full', m.dot, job.status === 'running' && 'animate-pulse')} />
        <span className="truncate font-mono text-[13px] text-ink">{job.scene}</span>
        <span className={cn('ml-auto shrink-0 font-mono text-[10px] uppercase tracking-wide', m.text)}>
          {job.status === 'queued' && queuePos ? `en cola #${queuePos}` : m.label}
        </span>
      </div>
      {curso && (
        <span className="truncate pl-4 text-[11px] text-muted" title={curso.name}>
          {curso.label}
        </span>
      )}
      <div className="flex items-center gap-1.5 pl-4 font-mono text-[11px] text-muted">
        <span>{job.quality}</span>
        <span className="text-faint" aria-hidden="true">·</span>
        <span>{fmtTime(job.created_at)}</span>
        {duration(job) && (<><span className="text-faint" aria-hidden="true">·</span><span>{duration(job)}</span></>)}
      </div>
      {active ? (
        <ChipAction danger onClick={() => onCancel(job.id)}>
          <X className="h-3 w-3" /> Cancelar
        </ChipAction>
      ) : (
        <div className="mt-0.5 flex items-center gap-1">
          <ChipAction onClick={() => onRetry(job.id)} title="volver a renderizar con el mismo script">
            <RotateCcw className="h-3 w-3" /> Reintentar
          </ChipAction>
          {arming ? (
            <ChipAction danger onClick={() => { setArming(false); onDelete(job.id) }}
              title={job.status === 'done' ? 'borra tambien el video' : 'borrar del historial'}>
              ¿Confirmar?
            </ChipAction>
          ) : (
            <ChipAction danger onClick={() => setArming(true)}
              title={job.status === 'done' ? 'borra tambien el video' : 'borrar del historial'}>
              <Trash2 className="h-3 w-3" /> Borrar
            </ChipAction>
          )}
        </div>
      )}
    </div>
  )
}

// Vaciar historial en dos toques; borra tambien los videos, y se dice.
function ClearHistoryButton({ count, onFire }) {
  const [arming, setArming] = useState(false)
  useEffect(() => {
    if (!arming) return
    const t = setTimeout(() => setArming(false), 4000)
    return () => clearTimeout(t)
  }, [arming])
  return arming ? (
    <span className="inline-flex items-center gap-1.5">
      <Button size="xs" variant="danger" onClick={() => { setArming(false); onFire() }}>
        ¿Borrar {count} (videos incluidos)?
      </Button>
      <Button size="xs" variant="ghost" onClick={() => setArming(false)}>No</Button>
    </span>
  ) : (
    <Button size="xs" variant="ghost" onClick={() => setArming(true)}
      title="borra todos los renders terminados, videos incluidos">
      <Trash2 className="h-3.5 w-3.5" /> Vaciar historial
    </Button>
  )
}

export default function Studio({ jobs, liveLog, resetLiveLog, onJobsChanged, aiEnabled,
  pendingScript, pendingScene, onConsumePendingScript, clipContext, onExitClip,
  onOpenProject }) {
  const temaEditor = useEditorTheme()   // CodeMirror sigue al tema de la app
  const [script, setScript] = useState(() => lsGet(LS.script) ?? SAMPLE)
  const [scenes, setScenes] = useState(() => [lsGet(LS.scene) || 'Orbita'])
  const [scene, setScene] = useState(() => lsGet(LS.scene) || 'Orbita')
  const [sceneError, setSceneError] = useState('')
  const [quality, setQuality] = useState(() => {
    const q = lsGet(LS.quality)
    return QUALITIES.some((o) => o.id === q) ? q : 'ql'
  })
  const [timeoutS, setTimeoutS] = useState(() => {
    const t = Number(lsGet(LS.timeout))
    return t >= 30 && t <= 1800 ? t : 600
  })
  const [submitError, setSubmitError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [savingClip, setSavingClip] = useState(false)
  const [clipSaved, setClipSaved] = useState(false)
  const [selectedId, setSelectedId] = useState(null)
  const [selectedLogs, setSelectedLogs] = useState([])
  const [aiOpen, setAiOpen] = useState(false)
  const [aiMode, setAiMode] = useState('explain')
  const [aiAutoRun, setAiAutoRun] = useState(0)
  const [confirmScript, setConfirmScript] = useState(null) // {script, scene} entrante a confirmar
  const logRef = useRef(null)
  const debounceRef = useRef(null)
  // Nombres de curso para la tira de renders (una sola copia para toda la app).
  const catalogo = useCatalogo()

  // Toda accion que pisa el editor (Abrir en el Estudio, Cargar al editor,
  // Aplicar de la IA) pasa por aqui: si hay trabajo propio, pide confirmacion.
  // nextScene es opcional (solo lo trae el flujo "Editar en Estudio" de un
  // clip, para preseleccionar su escena real).
  const replaceScript = useCallback((next, nextScene) => {
    const cur = script.trim()
    if (!cur || cur === next.trim() || cur === SAMPLE.trim()) {
      setScript(next)
      if (nextScene) setScene(nextScene)
    } else {
      setConfirmScript({ script: next, scene: nextScene })
    }
  }, [script])

  // Una animacion (o un clip de Proyectos) abierto reemplaza el editor una
  // sola vez; pendingScene solo viaja desde el flujo de clips.
  useEffect(() => {
    if (pendingScript == null) return
    replaceScript(pendingScript, pendingScene)
    onConsumePendingScript()
  }, [pendingScript, pendingScene, onConsumePendingScript, replaceScript])

  // Guardado local del script con debounce (una escritura por pausa de tipeo).
  useEffect(() => {
    const t = setTimeout(() => lsSet(LS.script, script), 400)
    return () => clearTimeout(t)
  }, [script])

  useEffect(() => {
    lsSet(LS.scene, scene)
    lsSet(LS.quality, quality)
    lsSet(LS.timeout, String(timeoutS))
  }, [scene, quality, timeoutS])

  // Deteccion de escenas con debounce (el backend usa ast, nunca ejecuta).
  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      try {
        const d = await api.scenes(script)
        setScenes(d.scenes)
        setSceneError(d.scenes.length ? '' : 'El script no define ninguna Scene')
        if (d.scenes.length && !d.scenes.includes(scene)) setScene(d.scenes[0])
      } catch (err) {
        setScenes([])
        setSceneError(err.message)
      }
    }, 700)
    return () => clearTimeout(debounceRef.current)
  }, [script]) // eslint-disable-line react-hooks/exhaustive-deps

  const selected = jobs.find((j) => j.id === selectedId) || jobs[0] || null

  // Logs del job seleccionado: snapshot HTTP + solo lineas SSE posteriores
  // (resetLiveLog descarta lo acumulado antes del snapshot para no duplicar).
  useEffect(() => {
    if (!selected) return
    let alive = true
    api.getJob(selected.id).then((d) => {
      if (!alive) return
      setSelectedLogs(d.logs)
      resetLiveLog(selected.id)
    }).catch(() => {})
    return () => { alive = false }
  }, [selected?.id, selected?.status]) // eslint-disable-line react-hooks/exhaustive-deps

  const logs = selected && liveLog.jobId === selected.id && selected.status === 'running'
    ? [...selectedLogs, ...liveLog.lines].slice(-5000)
    : selectedLogs

  // Autoscroll del registro SOLO si ya estabas al fondo: antes cada linea
  // nueva te arrastraba abajo y era imposible subir a leer un traceback
  // mientras el render seguia escribiendo.
  const atBottomRef = useRef(true)
  const onLogScroll = () => {
    const el = logRef.current
    if (el) atBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 24
  }
  useEffect(() => {
    if (logRef.current && atBottomRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
  }, [logs.length])
  // Al cambiar de job se vuelve a seguir el fondo.
  useEffect(() => { atBottomRef.current = true }, [selected?.id])

  // En contexto de clip el render no pasa por /api/jobs: primero se guarda
  // el script/escena en el clip (mismo endpoint que "Guardar en clip") y
  // luego se dispara el render propio del clip, que compone el estilo del
  // proyecto en el backend y hereda su calidad fija.
  const submit = useCallback(async () => {
    setSubmitError('')
    setSubmitting(true) // evita el doble encolado por doble clic
    try {
      let job
      if (clipContext) {
        await api.patchClip(clipContext.projectId, clipContext.clipId, { script, scene })
        job = await api.renderClip(clipContext.projectId, clipContext.clipId)
      } else {
        job = await api.createJob({ script, scene, quality, timeout: Number(timeoutS) })
      }
      setSelectedId(job.id)
      onJobsChanged()
    } catch (err) {
      setSubmitError(err.message)
    } finally {
      setSubmitting(false)
    }
  }, [script, scene, quality, timeoutS, onJobsChanged, clipContext])

  // Boton "Guardar en clip": guarda sin renderizar (patchClip {script, scene}).
  const saveClip = async () => {
    if (!clipContext) return
    setSubmitError('')
    setSavingClip(true)
    setClipSaved(false)
    try {
      await api.patchClip(clipContext.projectId, clipContext.clipId, { script, scene })
      setClipSaved(true)
      setTimeout(() => setClipSaved(false), 2500)
    } catch (err) {
      setSubmitError(err.message)
    } finally {
      setSavingClip(false)
    }
  }

  // Cancelar puede fallar de verdad (el runner caido, p.ej.): antes el error
  // se tragaba en silencio y el chip se quedaba "renderizando" sin explicacion.
  const cancel = async (id) => {
    setSubmitError('')
    try {
      await api.cancelJob(id)
    } catch (err) {
      if (err.status !== 404 && err.status !== 409) setSubmitError(`No se pudo cancelar: ${err.message}`)
    }
  }

  const retry = async (id) => {
    setSubmitError('')
    try {
      const job = await api.retryJob(id)
      setSelectedId(job.id)
      onJobsChanged()
    } catch (err) {
      setSubmitError(err.message)
    }
  }

  const removeJob = async (id) => {
    setSubmitError('')
    try {
      await api.deleteJob(id)
      if (selectedId === id) setSelectedId(null)
      onJobsChanged()
    } catch (err) {
      setSubmitError(err.message)
    }
  }

  const clearHistory = async () => {
    setSubmitError('')
    try {
      await api.deleteFinishedJobs()
      setSelectedId(null)
      onJobsChanged()
    } catch (err) {
      setSubmitError(err.message)
    }
  }

  const loadScript = async (id) => {
    try {
      const d = await api.getScript(id)
      if (d.script) replaceScript(d.script)
    } catch { /* sin script */ }
  }

  const canSubmit = scenes.includes(scene) && !submitting
  const submitHint = !scenes.includes(scene)
    ? 'Define una Scene valida en el script para renderizar'
    : clipContext
      ? 'Guarda el clip y encola su render (compone el estilo del proyecto) · Ctrl+Enter'
      : 'Encolar el render (se ejecutan de a uno) · Ctrl+Enter'
  const errorish = selected && ['error', 'timeout'].includes(selected.status)
  const cursoSel = selected && cursoDeJob(selected, catalogo)
  // Nota de desfase de líneas: los errores de escenas/render pueden citar
  // numeros de linea del script COMPUESTO (estilo + clip), que no coinciden
  // con los del editor (que solo muestra el script del clip).
  const styleNote = clipContext && clipContext.styleOffset > 0
    ? `El estilo del proyecto añade ${clipContext.styleOffset} líneas antes del script; los numeros de linea de arriba pueden estar desplazados.`
    : ''

  // Tira inferior: cola activa (running + queued en orden de ejecucion) y
  // historial reciente por separado — antes se mezclaban bajo un solo rotulo.
  const activeJobs = jobs
    .filter((j) => ['queued', 'running'].includes(j.status))
    .sort((a, b) => a.created_at - b.created_at)
  const queuedIds = activeJobs.filter((j) => j.status === 'queued').map((j) => j.id)
  const historyJobs = jobs.filter((j) => !['queued', 'running'].includes(j.status))
  const queueLabel = activeJobs.length === 0
    ? 'libre'
    : [
        activeJobs.some((j) => j.status === 'running') && '1 renderizando',
        queuedIds.length > 0 && `${queuedIds.length} en espera`,
      ].filter(Boolean).join(' · ')

  return (
    <main data-view="studio" className="flex flex-1 flex-col gap-3 p-3 lg:min-h-0">
      {/* Contexto de clip: se llega aqui desde "Editar en Estudio" de un
          proyecto. La calidad queda fija a la del proyecto y el render usa
          el endpoint del clip (compone el estilo) en vez de /api/jobs. */}
      {clipContext && (
        <div className="panel flex shrink-0 flex-wrap items-center gap-2 px-3 py-2" aria-label="contexto de clip">
          <FolderKanban className="h-4 w-4 shrink-0 text-accent" />
          <span className="text-[13px] text-ink">
            Proyecto <strong className="font-semibold">{clipContext.projectName}</strong>
            {' · clip "'}<strong className="font-semibold">{clipContext.clipTitle}</strong>{'"'}
            {' · calidad '}{QUALITY_LABEL[clipContext.quality] || clipContext.quality}{' (fija)'}
          </span>
          {/* Sin esto el viaje de vuelta era: nav Proyectos → volvias a la
              LISTA (la ruta perdio el id al navegar al Estudio) → buscar el
              curso entre ~60 → abrirlo. */}
          <Button size="xs" variant="default" className="ml-auto"
            onClick={() => onOpenProject?.(clipContext.projectId)}
            title="Volver al proyecto sin salir del contexto del clip">
            <ArrowLeft className="h-3.5 w-3.5" /> Volver al proyecto
          </Button>
          <Button size="xs" variant="ghost" onClick={onExitClip}
            title="Vuelve al render libre; no borra el script del editor">
            <LogOut className="h-3.5 w-3.5" /> Salir del clip
          </Button>
        </div>
      )}
      {/* En movil cada panel fija su altura (la pagina scrollea); en lg+ el
          conjunto llena el viewport y cada panel scrollea por dentro. */}
      <div className="flex flex-col gap-3 lg:min-h-0 lg:flex-1 lg:flex-row">
        {/* ── Editor ── */}
        {/* Ctrl/⌘+Enter renderiza desde el editor: el bucle real es
            escribir → render → leer log → corregir, y bajar el raton al boton
            en cada vuelta sobra. El handler va en la seccion (no en window)
            para que no dispare desde otras vistas, que siguen montadas. */}
        <section className="panel flex h-[62dvh] min-w-0 flex-col overflow-hidden lg:h-auto lg:min-h-0 lg:flex-1" aria-label="editor"
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
              e.preventDefault()
              if (canSubmit) submit()
            }
          }}>
          <div className="flex flex-wrap items-center gap-2 border-b border-line px-3 py-2">
            <div className="flex items-center gap-2">
              <FileCode className="h-4 w-4 text-muted" />
              <span className="font-mono text-[13px] text-ink">escena.py</span>
              <MarcaChip script={script} />
            </div>
            <div className="mx-1 hidden h-5 w-px bg-line sm:block" />
            <label className="flex items-center gap-1.5">
              <span className="eyebrow">Escena</span>
              <Select value={scene} onValueChange={setScene} disabled={!scenes.length}>
                <SelectTrigger className="h-8 w-[150px]">
                  <SelectValue placeholder="—" />
                </SelectTrigger>
                <SelectContent>
                  {scenes.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </label>

            <div className="ml-auto flex flex-wrap items-center gap-2">
              <Segmented options={QUALITIES}
                value={clipContext ? clipContext.quality : quality}
                onChange={clipContext ? () => {} : setQuality} ariaLabel="calidad"
                disabled={!!clipContext} />
              <label className="flex items-center gap-1.5">
                <span className="eyebrow">Timeout</span>
                {/* Se normaliza al salir del campo: vaciarlo mandaba NaN a la
                    API y el error solo llegaba del servidor tras encolar. */}
                <input type="number" min="30" max="1800" step="30" value={timeoutS}
                  onChange={(e) => setTimeoutS(e.target.value)}
                  onBlur={(e) => {
                    const n = Number(e.target.value)
                    setTimeoutS(Number.isFinite(n) ? Math.min(1800, Math.max(30, Math.round(n))) : 600)
                  }}
                  className="h-8 w-[68px] rounded-md border border-line bg-canvas px-2 text-sm tabular-nums text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan" />
                <span className="text-xs text-faint">s</span>
              </label>
              {aiEnabled && (
                <Button variant="accent" size="sm" title="asistente IA (Gemini 2.5)"
                  onClick={() => { setAiMode('generate'); setAiOpen(true) }}>
                  <Sparkles className="h-4 w-4" /> Asistente
                </Button>
              )}
              {clipContext && (
                <Button variant="default" size="sm" onClick={saveClip} disabled={savingClip}
                  title="Guarda el script y la escena en el clip sin renderizar">
                  <Save className="h-4 w-4" /> {savingClip ? 'Guardando…' : clipSaved ? 'Guardado ✓' : 'Guardar en clip'}
                </Button>
              )}
              <Button variant="primary" size="sm" onClick={submit} disabled={!canSubmit}
                title={submitHint}>
                <Play className="h-4 w-4" /> {submitting ? 'Encolando…' : 'Renderizar'}
              </Button>
            </div>
          </div>

          {(sceneError || submitError) && (
            <p role="alert" className="border-b border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">
              {sceneError || submitError}
              {styleNote && <span className="mt-0.5 block text-[12px] text-warn/80">{styleNote}</span>}
            </p>
          )}

          <CodeMirror
            value={script}
            onChange={setScript}
            extensions={[python()]}
            theme={temaEditor}
            height="100%"
            className="editor min-h-0 flex-1 overflow-auto text-[13px]"
            basicSetup={{ foldGutter: false, highlightActiveLine: true }}
          />
        </section>

        {/* ── Rail de resultado ── */}
        <aside className="flex w-full flex-col gap-3 lg:min-h-0 lg:w-[440px] lg:shrink-0" aria-label="resultado">
          {selected?.status === 'done' && (
            <div className="panel shrink-0 overflow-hidden">
              <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
                <span className="eyebrow truncate" title={cursoSel?.name}>
                  Resultado · {cursoSel ? `${cursoSel.label} · ` : ''}{selected.scene}
                </span>
                <a href={videoUrl(selected.id)} download={`${selected.scene}.mp4`}
                  className="inline-flex shrink-0 items-center gap-1.5 text-xs text-muted transition-colors hover:text-ink">
                  <Download className="h-3.5 w-3.5" /> MP4
                </a>
              </div>
              <video key={selected.id} className="block w-full bg-black" controls preload="metadata"
                src={videoUrl(selected.id)} />
            </div>
          )}

          <div className="panel flex h-[45dvh] flex-col overflow-hidden lg:h-auto lg:min-h-0 lg:flex-1">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
              <span className="eyebrow truncate" title={cursoSel?.name}>
                Registro{selected ? ` · ${cursoSel ? `${cursoSel.label} · ` : ''}${selected.scene} (${selected.id.slice(0, 8)})` : ''}
              </span>
              {selected && (
                <div className="flex items-center gap-1.5">
                  {aiEnabled && errorish && (
                    <Button size="xs" variant="accent"
                      onClick={() => { setAiMode('explain'); setAiOpen(true); setAiAutoRun((n) => n + 1) }}>
                      <Sparkles className="h-3.5 w-3.5" /> Explicar
                    </Button>
                  )}
                  {aiEnabled && errorish && (
                    <Button size="xs" variant="accent"
                      onClick={() => { setAiMode('fix'); setAiOpen(true) }}>
                      <Wrench className="h-3.5 w-3.5" /> Corregir
                    </Button>
                  )}
                  <Button size="xs" variant="ghost" onClick={() => loadScript(selected.id)}>
                    Cargar al editor
                  </Button>
                </div>
              )}
            </div>
            <pre ref={logRef} onScroll={onLogScroll}
              className="m-0 min-h-0 flex-1 overflow-auto whitespace-pre-wrap break-words rounded-b-[13px] bg-canvas px-3 py-2.5 font-mono text-[11.5px] leading-relaxed text-code-ink">
              {logs.length ? logs.join('\n')
                : selected?.status === 'queued' ? 'En cola — esperando su turno (1 render a la vez)…'
                : selected?.error ? `✕ ${selected.error}`
                : 'Sin registro.'}
              {selected?.status !== 'running' && selected?.error && logs.length
                ? `\n✕ ${selected.error}` : ''}
            </pre>
          </div>
        </aside>
      </div>

      {/* ── Tira inferior: cola activa + historial reciente ── */}
      <div className="panel shrink-0 overflow-hidden">
        <div className="flex flex-wrap items-center gap-2 border-b border-line px-3 py-1.5">
          <span className="eyebrow">Cola</span>
          <span className="font-mono text-[11px] text-faint">{queueLabel}</span>
          <span className="mx-1 h-4 w-px bg-line" aria-hidden="true" />
          <span className="eyebrow">Historial</span>
          <span className="font-mono text-[11px] text-faint">{historyJobs.length}</span>
          {historyJobs.length > 0 && (
            <span className="ml-auto">
              <ClearHistoryButton count={historyJobs.length} onFire={clearHistory} />
            </span>
          )}
        </div>
        {jobs.length === 0 ? (
          <p className="px-3 py-3 text-[13px] text-muted">
            Sin renders todavía. Escribe una escena y pulsa Renderizar.
          </p>
        ) : (
          <div className="flex items-stretch gap-2 overflow-x-auto px-3 py-2.5">
            {activeJobs.map((j) => (
              <JobChip key={j.id} job={j} curso={cursoDeJob(j, catalogo)}
                selected={selected?.id === j.id}
                queuePos={j.status === 'queued' ? queuedIds.indexOf(j.id) + 1 : null}
                onSelect={() => setSelectedId(j.id)} onCancel={cancel} />
            ))}
            {activeJobs.length > 0 && historyJobs.length > 0 && (
              <span className="mx-1 w-px shrink-0 self-stretch bg-line" aria-hidden="true" />
            )}
            {historyJobs.slice(0, 20).map((j) => (
              <JobChip key={j.id} job={j} curso={cursoDeJob(j, catalogo)}
                selected={selected?.id === j.id}
                onSelect={() => setSelectedId(j.id)}
                onCancel={cancel} onRetry={retry} onDelete={removeJob} />
            ))}
          </div>
        )}
      </div>

      {aiEnabled && (
        <Assistant open={aiOpen} mode={aiMode} onMode={setAiMode}
          onClose={() => setAiOpen(false)} job={selected} jobLogs={logs}
          autoRun={aiAutoRun} onApply={replaceScript} />
      )}

      {/* Confirmacion antes de pisar trabajo propio en el editor. */}
      <Dialog open={confirmScript != null} onOpenChange={(o) => !o && setConfirmScript(null)}>
        <DialogContent className="w-[min(420px,94vw)] p-5" showClose={false}>
          <DialogTitle className="font-display text-[15px] font-semibold text-ink">
            ¿Reemplazar el contenido del editor?
          </DialogTitle>
          <p className="mt-2 text-[13px] leading-relaxed text-muted">
            El script actual del editor se descartará. Si quieres conservarlo,
            cancela y cópialo antes.
          </p>
          <div className="mt-4 flex justify-end gap-2">
            <Button variant="ghost" onClick={() => {
              // Si el pendingScript traia un clipContext (viene de "Editar en
              // Estudio") y el usuario decide conservar su script propio, el
              // contexto de clip debe apagarse: si no, "Guardar en clip" o
              // "Renderizar" sobrescribirian el clip ajeno con este script.
              if (clipContext) onExitClip()
              setConfirmScript(null)
            }}>Conservar</Button>
            <Button variant="primary"
              onClick={() => {
                setScript(confirmScript.script)
                if (confirmScript.scene) setScene(confirmScript.scene)
                setConfirmScript(null)
              }}>
              Reemplazar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  )
}
