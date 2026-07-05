import { useCallback, useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { api, videoUrl } from './api.js'
import Assistant from './Assistant.jsx'

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

const STATUS_LABEL = {
  queued: 'en cola', running: 'renderizando', done: 'listo',
  error: 'error', cancelled: 'cancelado', timeout: 'timeout',
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

export default function Studio({ jobs, liveLog, resetLiveLog, onJobsChanged, aiEnabled }) {
  const [script, setScript] = useState(SAMPLE)
  const [scenes, setScenes] = useState(['Orbita'])
  const [scene, setScene] = useState('Orbita')
  const [sceneError, setSceneError] = useState('')
  const [quality, setQuality] = useState('ql')
  const [timeoutS, setTimeoutS] = useState(600)
  const [submitError, setSubmitError] = useState('')
  const [selectedId, setSelectedId] = useState(null)
  const [selectedLogs, setSelectedLogs] = useState([])
  const [aiOpen, setAiOpen] = useState(false)
  const [aiMode, setAiMode] = useState('explain')
  const [aiAutoRun, setAiAutoRun] = useState(0)
  const logRef = useRef(null)
  const debounceRef = useRef(null)

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

  return (
    <main className="studio">
      <section className="panel panel--editor" aria-label="editor">
        <div className="panel__bar">
          <span className="panel__title">ESCENA.PY</span>
          <div className="controls">
            <label className="ctl">
              <span>Escena</span>
              <select value={scene} onChange={(e) => setScene(e.target.value)}
                disabled={!scenes.length}>
                {scenes.map((s) => <option key={s}>{s}</option>)}
              </select>
            </label>
            <div className="seg" role="radiogroup" aria-label="calidad">
              {QUALITIES.map((q) => (
                <button key={q.id} title={q.hint}
                  className={quality === q.id ? 'seg__opt seg__opt--on' : 'seg__opt'}
                  onClick={() => setQuality(q.id)}>{q.label}</button>
              ))}
            </div>
            <label className="ctl">
              <span>Timeout</span>
              <input type="number" min="30" max="1800" step="30" value={timeoutS}
                onChange={(e) => setTimeoutS(e.target.value)} />
            </label>
            <button className="btn btn--primary" onClick={submit} disabled={!canSubmit}>
              Renderizar
            </button>
            {aiEnabled && (
              <button className="btn" title="asistente IA (Gemini 2.5)"
                onClick={() => { setAiMode('generate'); setAiOpen(true) }}>
                ✨ Asistente
              </button>
            )}
          </div>
        </div>
        {(sceneError || submitError) && (
          <p className="notice notice--warn" role="alert">{sceneError || submitError}</p>
        )}
        <CodeMirror
          value={script}
          onChange={setScript}
          extensions={[python()]}
          theme="dark"
          height="100%"
          className="editor"
          basicSetup={{ foldGutter: false, highlightActiveLine: true }}
        />
      </section>

      <section className="side">
        <div className="panel panel--queue" aria-label="cola de renders">
          <div className="panel__bar"><span className="panel__title">COLA DE RENDERS</span></div>
          {jobs.length === 0 && (
            <p className="empty">Sin renders todavía. Escribe una escena y pulsa Renderizar.</p>
          )}
          <ul className="jobs">
            {jobs.slice(0, 12).map((j) => (
              <li key={j.id}
                className={`job ${selected?.id === j.id ? 'job--sel' : ''}`}
                onClick={() => setSelectedId(j.id)}>
                <span className={`dot dot--${j.status}`} aria-hidden="true" />
                <span className="job__scene">{j.scene}</span>
                <span className="job__meta">{j.quality} · {fmtTime(j.created_at)}
                  {duration(j) ? ` · ${duration(j)}` : ''}</span>
                <span className={`job__status job__status--${j.status}`}>
                  {STATUS_LABEL[j.status] || j.status}
                </span>
                {['queued', 'running'].includes(j.status) && (
                  <button className="btn btn--tiny"
                    onClick={(e) => { e.stopPropagation(); cancel(j.id) }}>
                    Cancelar
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className="panel panel--log" aria-label="registro del render">
          <div className="panel__bar">
            <span className="panel__title">
              REGISTRO {selected ? `· ${selected.scene} (${selected.id.slice(0, 8)})` : ''}
            </span>
            {selected && (
              <span className="panel__actions">
                {aiEnabled && ['error', 'timeout'].includes(selected.status) && (
                  <button className="btn btn--tiny btn--ai"
                    onClick={() => {
                      setAiMode('explain'); setAiOpen(true)
                      setAiAutoRun((n) => n + 1)
                    }}>
                    ✨ Explicar error
                  </button>
                )}
                {aiEnabled && ['error', 'timeout'].includes(selected.status) && (
                  <button className="btn btn--tiny btn--ai"
                    onClick={() => { setAiMode('fix'); setAiOpen(true) }}>
                    🔧 Corregir con IA
                  </button>
                )}
                <button className="btn btn--tiny" onClick={() => loadScript(selected.id)}>
                  Cargar script al editor
                </button>
              </span>
            )}
          </div>
          <pre className="log" ref={logRef}>
            {logs.length ? logs.join('\n')
              : selected?.status === 'queued' ? 'En cola — esperando su turno (1 render a la vez)…'
              : selected?.error ? `✕ ${selected.error}`
              : 'Sin registro.'}
            {selected?.status !== 'running' && selected?.error && logs.length
              ? `\n✕ ${selected.error}` : ''}
          </pre>
        </div>

        {selected?.status === 'done' && (
          <div className="panel panel--video" aria-label="previsualizacion">
            <div className="panel__bar">
              <span className="panel__title">RESULTADO</span>
              <a className="btn btn--tiny" href={videoUrl(selected.id)}
                download={`${selected.scene}.mp4`}>Descargar MP4</a>
            </div>
            <video key={selected.id} className="video" controls preload="metadata"
              src={videoUrl(selected.id)} />
          </div>
        )}
      </section>

      {aiEnabled && (
        <Assistant open={aiOpen} mode={aiMode} onMode={setAiMode}
          onClose={() => setAiOpen(false)} job={selected} jobLogs={logs}
          autoRun={aiAutoRun} onApply={setScript} />
      )}
    </main>
  )
}
