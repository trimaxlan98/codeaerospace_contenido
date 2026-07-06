import { useCallback, useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { Play, Sparkles, Wrench, Download, FileCode, X } from 'lucide-react'
import { api, videoUrl } from './api.js'
import Assistant from './Assistant.jsx'
import { Button } from './components/ui/button.jsx'
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

// Ficha de la tira de cola. Div interactivo (el boton Cancelar anida dentro).
function JobChip({ job, selected, onSelect, onCancel }) {
  const m = STATUS_META[job.status] || STATUS_META.default
  const active = ['queued', 'running'].includes(job.status)
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
        <span className={cn('ml-auto shrink-0 font-mono text-[10px] uppercase tracking-wide', m.text)}>{m.label}</span>
      </div>
      <div className="flex items-center gap-1.5 pl-4 font-mono text-[11px] text-muted">
        <span>{job.quality}</span>
        <span className="text-faint">·</span>
        <span>{fmtTime(job.created_at)}</span>
        {duration(job) && (<><span className="text-faint">·</span><span>{duration(job)}</span></>)}
      </div>
      {active && (
        <button type="button"
          onClick={(e) => { e.stopPropagation(); onCancel(job.id) }}
          className="mt-0.5 inline-flex w-fit items-center gap-1 rounded px-1.5 py-0.5 text-[11px] text-muted transition-colors hover:bg-err/10 hover:text-err">
          <X className="h-3 w-3" /> Cancelar
        </button>
      )}
    </div>
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
  const [selectedId, setSelectedId] = useState(null)
  const [selectedLogs, setSelectedLogs] = useState([])
  const [aiOpen, setAiOpen] = useState(false)
  const [aiMode, setAiMode] = useState('explain')
  const [aiAutoRun, setAiAutoRun] = useState(0)
  const logRef = useRef(null)
  const debounceRef = useRef(null)

  // Una animacion abierta desde la Biblioteca reemplaza el editor una sola vez.
  useEffect(() => {
    if (pendingScript == null) return
    setScript(pendingScript)
    onConsumePendingScript()
  }, [pendingScript, onConsumePendingScript])

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
    try {
      const job = await api.createJob({ script, scene, quality, timeout: Number(timeoutS) })
      setSelectedId(job.id)
      onJobsChanged()
    } catch (err) {
      setSubmitError(err.message)
    }
  }, [script, scene, quality, timeoutS, onJobsChanged])

  const cancel = async (id) => {
    try { await api.cancelJob(id) } catch { /* ya termino */ }
  }

  const loadScript = async (id) => {
    try {
      const d = await api.getScript(id)
      if (d.script) setScript(d.script)
    } catch { /* sin script */ }
  }

  const canSubmit = scenes.includes(scene) && !jobs.some((j) => j.status === 'queued')
  const errorish = selected && ['error', 'timeout'].includes(selected.status)

  return (
    <main className="flex min-h-0 flex-1 flex-col gap-3 p-3">
      <div className="flex min-h-0 flex-1 flex-col gap-3 lg:flex-row">
        {/* ── Editor ── */}
        <section className="panel flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden" aria-label="editor">
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
              <Button variant="primary" size="sm" onClick={submit} disabled={!canSubmit}>
                <Play className="h-4 w-4" /> Renderizar
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
        <aside className="flex min-h-0 w-full shrink-0 flex-col gap-3 lg:w-[440px]" aria-label="resultado">
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

          <div className="panel flex min-h-0 flex-1 flex-col overflow-hidden">
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

      {/* ── Tira de cola (horizontal, sin scroll vertical diminuto) ── */}
      <div className="panel shrink-0 overflow-hidden">
        <div className="flex items-center gap-2 border-b border-line px-3 py-1.5">
          <span className="eyebrow">Cola de renders</span>
          <span className="font-mono text-[11px] text-faint">{jobs.length}</span>
        </div>
        {jobs.length === 0 ? (
          <p className="px-3 py-3 text-[13px] text-muted">
            Sin renders todavía. Escribe una escena y pulsa Renderizar.
          </p>
        ) : (
          <div className="flex gap-2 overflow-x-auto px-3 py-2.5">
            {jobs.slice(0, 20).map((j) => (
              <JobChip key={j.id} job={j} selected={selected?.id === j.id}
                onSelect={() => setSelectedId(j.id)} onCancel={cancel} />
            ))}
          </div>
        )}
      </div>

      {aiEnabled && (
        <Assistant open={aiOpen} mode={aiMode} onMode={setAiMode}
          onClose={() => setAiOpen(false)} job={selected} jobLogs={logs}
          autoRun={aiAutoRun} onApply={setScript} />
      )}
    </main>
  )
}
