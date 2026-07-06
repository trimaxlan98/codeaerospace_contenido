import { useCallback, useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { Play, Sparkles, Wrench, Download, FileCode, RotateCcw, Trash2, X } from 'lucide-react'
import { api, videoUrl } from './api.js'
import Assistant from './Assistant.jsx'
import { Button } from './components/ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select.jsx'
import { cn } from '@/lib/utils'

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
function Segmented({ options, value, onChange, ariaLabel }) {
  return (
    <div role="radiogroup" aria-label={ariaLabel}
      className="flex rounded-md border border-line bg-canvas p-0.5">
      {options.map((o) => {
        const on = value === o.id
        return (
          <button key={o.id} type="button" role="radio" aria-checked={on} title={o.hint}
            onClick={() => onChange(o.id)}
            className={cn(
              'rounded-[5px] px-2.5 py-1 font-mono text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
              on ? 'bg-surface-2 text-accent shadow-sm' : 'text-muted hover:text-ink',
            )}>
            {o.label}
          </button>
        )
      })}
    </div>
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
function JobChip({ job, selected, onSelect, onCancel, onRetry, onDelete, queuePos }) {
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
      <div className="flex items-center gap-1.5 pl-4 font-mono text-[11px] text-muted">
        <span>{job.quality}</span>
        <span className="text-faint">·</span>
        <span>{fmtTime(job.created_at)}</span>
        {duration(job) && (<><span className="text-faint">·</span><span>{duration(job)}</span></>)}
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
  pendingScript, onConsumePendingScript }) {
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
  const [selectedId, setSelectedId] = useState(null)
  const [selectedLogs, setSelectedLogs] = useState([])
  const [aiOpen, setAiOpen] = useState(false)
  const [aiMode, setAiMode] = useState('explain')
  const [aiAutoRun, setAiAutoRun] = useState(0)
  const [confirmScript, setConfirmScript] = useState(null) // script entrante a confirmar
  const logRef = useRef(null)
  const debounceRef = useRef(null)

  // Toda accion que pisa el editor (Abrir en el Estudio, Cargar al editor,
  // Aplicar de la IA) pasa por aqui: si hay trabajo propio, pide confirmacion.
  const replaceScript = useCallback((next) => {
    const cur = script.trim()
    if (!cur || cur === next.trim() || cur === SAMPLE.trim()) setScript(next)
    else setConfirmScript(next)
  }, [script])

  // Una animacion abierta desde Animaciones reemplaza el editor una sola vez.
  useEffect(() => {
    if (pendingScript == null) return
    replaceScript(pendingScript)
    onConsumePendingScript()
  }, [pendingScript, onConsumePendingScript, replaceScript])

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

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
  }, [logs.length])

  const submit = useCallback(async () => {
    setSubmitError('')
    setSubmitting(true) // evita el doble encolado por doble clic
    try {
      const job = await api.createJob({ script, scene, quality, timeout: Number(timeoutS) })
      setSelectedId(job.id)
      onJobsChanged()
    } catch (err) {
      setSubmitError(err.message)
    } finally {
      setSubmitting(false)
    }
  }, [script, scene, quality, timeoutS, onJobsChanged])

  const cancel = async (id) => {
    try { await api.cancelJob(id) } catch { /* ya termino */ }
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
    : 'Encolar el render (se ejecutan de a uno)'
  const errorish = selected && ['error', 'timeout'].includes(selected.status)

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
    <main className="flex flex-1 flex-col gap-3 p-3 lg:min-h-0">
      {/* En movil cada panel fija su altura (la pagina scrollea); en lg+ el
          conjunto llena el viewport y cada panel scrollea por dentro. */}
      <div className="flex flex-col gap-3 lg:min-h-0 lg:flex-1 lg:flex-row">
        {/* ── Editor ── */}
        <section className="panel flex h-[62dvh] min-w-0 flex-col overflow-hidden lg:h-auto lg:min-h-0 lg:flex-1" aria-label="editor">
          <div className="flex flex-wrap items-center gap-2 border-b border-line px-3 py-2">
            <div className="flex items-center gap-2">
              <FileCode className="h-4 w-4 text-muted" />
              <span className="font-mono text-[13px] text-ink">escena.py</span>
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
              <Segmented options={QUALITIES} value={quality} onChange={setQuality} ariaLabel="calidad" />
              <label className="flex items-center gap-1.5">
                <span className="eyebrow">Timeout</span>
                <input type="number" min="30" max="1800" step="30" value={timeoutS}
                  onChange={(e) => setTimeoutS(e.target.value)}
                  className="h-8 w-[68px] rounded-md border border-line bg-canvas px-2 text-sm tabular-nums text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan" />
                <span className="text-xs text-faint">s</span>
              </label>
              {aiEnabled && (
                <Button variant="accent" size="sm" title="asistente IA (Gemini 2.5)"
                  onClick={() => { setAiMode('generate'); setAiOpen(true) }}>
                  <Sparkles className="h-4 w-4" /> Asistente
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
            </p>
          )}

          <CodeMirror
            value={script}
            onChange={setScript}
            extensions={[python()]}
            theme="dark"
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
                <span className="eyebrow truncate">Resultado · {selected.scene}</span>
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
              <span className="eyebrow truncate">
                Registro{selected ? ` · ${selected.scene} (${selected.id.slice(0, 8)})` : ''}
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
            <pre ref={logRef}
              className="m-0 min-h-0 flex-1 overflow-auto whitespace-pre-wrap break-words rounded-b-[13px] bg-canvas px-3 py-2.5 font-mono text-[11.5px] leading-relaxed text-[#a8bcd4]">
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
              <JobChip key={j.id} job={j} selected={selected?.id === j.id}
                queuePos={j.status === 'queued' ? queuedIds.indexOf(j.id) + 1 : null}
                onSelect={() => setSelectedId(j.id)} onCancel={cancel} />
            ))}
            {activeJobs.length > 0 && historyJobs.length > 0 && (
              <span className="mx-1 w-px shrink-0 self-stretch bg-line" aria-hidden="true" />
            )}
            {historyJobs.slice(0, 20).map((j) => (
              <JobChip key={j.id} job={j} selected={selected?.id === j.id}
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
            <Button variant="ghost" onClick={() => setConfirmScript(null)}>Conservar</Button>
            <Button variant="primary"
              onClick={() => { setScript(confirmScript); setConfirmScript(null) }}>
              Reemplazar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  )
}
