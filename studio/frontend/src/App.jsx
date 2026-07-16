import { useCallback, useEffect, useRef, useState } from 'react'
import { X } from 'lucide-react'
import { api, setUnauthorizedHandler } from './api.js'
import { useRoute } from './router.js'
import { cn } from '@/lib/utils'
import Login from './Login.jsx'
import Header from './Header.jsx'
import Studio from './Studio.jsx'
import Admin from './Admin.jsx'
import Library from './Library.jsx'
import Lessons from './Lessons.jsx'
import Animations from './Animations.jsx'
import StarfieldBackground from './components/StarfieldBackground.jsx'

const TOAST_META = {
  done: { label: 'listo', dot: 'bg-ok', text: 'text-ok' },
  error: { label: 'con error', dot: 'bg-err', text: 'text-err' },
  timeout: { label: 'timeout', dot: 'bg-err', text: 'text-err' },
  cancelled: { label: 'cancelado', dot: 'bg-muted', text: 'text-muted' },
}

export default function App() {
  const [auth, setAuth] = useState(null) // null=cargando, false=no, true=si
  const [aiEnabled, setAiEnabled] = useState(false)
  const [route, navigate] = useRoute()
  const view = route.view
  // Vistas keep-alive: se montan al visitarlas por primera vez y despues solo
  // se ocultan, para que su estado (editor, leccion abierta, tab de Admin…)
  // sobreviva a los cambios de pestana.
  const visited = useRef(new Set())
  visited.current.add(view)
  const [pendingScript, setPendingScript] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [containers, setContainers] = useState(null)
  const [jobs, setJobs] = useState([])
  const [storage, setStorage] = useState(null)
  const [liveLog, setLiveLog] = useState({ jobId: null, lines: [] })
  const [toasts, setToasts] = useState([]) // avisos de fin de render
  const [staleSince, setStaleSince] = useState(null) // ultimo evento SSE si el stream calla
  const esRef = useRef(null)
  const jobsRef = useRef([]) // espejo de jobs para leer el estado previo en el SSE
  const lastEventRef = useRef(Date.now())
  const lastProbeRef = useRef(0)

  useEffect(() => { jobsRef.current = jobs }, [jobs])

  // Sesion expirada: cualquier 401 de la API devuelve al login de inmediato
  // (antes cada accion fallaba con mensajes cripticos y nada redirigia).
  useEffect(() => { setUnauthorizedHandler(() => setAuth(false)) }, [])

  const pushToast = useCallback((job) => {
    const key = `${job.id}:${job.status}`
    setToasts((prev) => [...prev.filter((t) => t.key !== key).slice(-2), { key, job }])
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.key !== key)), 8000)
  }, [])
  const dismissToast = (key) => setToasts((prev) => prev.filter((t) => t.key !== key))

  // El visor de logs fija un snapshot HTTP y luego solo acumula lineas SSE
  // posteriores; este reset evita duplicados entre ambas fuentes.
  const resetLiveLog = useCallback((jobId) => {
    setLiveLog({ jobId, lines: [] })
  }, [])

  const refreshJobs = useCallback(async () => {
    try {
      const data = await api.listJobs()
      setJobs(data.jobs)
      if (data.storage) setStorage(data.storage)
    } catch { /* la sesion pudo expirar; lo detecta el proximo request */ }
  }, [])

  // Consulta /api/me: fija sesion y flags de IA en una sola pasada.
  const refreshMe = useCallback(async () => {
    try {
      const d = await api.me()
      setAuth(d.authenticated)
      setAiEnabled(Boolean(d.ai_enabled))
    } catch {
      setAuth(false)
    }
  }, [])

  useEffect(() => { refreshMe() }, [refreshMe]) // consulta inicial al montar

  // Stream SSE unico: metricas + estados de job + logs en vivo.
  useEffect(() => {
    if (auth !== true) return
    refreshJobs()
    lastEventRef.current = Date.now()
    setStaleSince(null)
    const es = new EventSource('/api/events')
    esRef.current = es
    es.onmessage = (msg) => {
      lastEventRef.current = Date.now()
      const ev = JSON.parse(msg.data)
      if (ev.type === 'metrics') {
        if (ev.host) setMetrics(ev.host)
        if (ev.containers !== undefined) setContainers(ev.containers)
      } else if (ev.type === 'job') {
        // Transicion a estado terminal → aviso (el SSE solo difunde cambios
        // reales, no hay catch-up al conectar).
        const terminal = !['queued', 'running'].includes(ev.job.status)
        const prev = jobsRef.current.find((j) => j.id === ev.job.id)
        if (terminal && (!prev || ['queued', 'running'].includes(prev.status))) pushToast(ev.job)
        setJobs((prev) => {
          const rest = prev.filter((j) => j.id !== ev.job.id)
          return [ev.job, ...rest].sort((a, b) => b.created_at - a.created_at)
        })
        // Al terminar un job cambia el uso de disco: refrescar cuota.
        if (terminal) refreshJobs()
      } else if (ev.type === 'joblog') {
        setLiveLog((prev) =>
          prev.jobId === ev.job_id
            ? { jobId: ev.job_id, lines: [...prev.lines.slice(-4999), ev.line] }
            : { jobId: ev.job_id, lines: [ev.line] },
        )
      }
    }
    es.onerror = () => {
      // EventSource reintenta solo, pero no expone el 401: si el stream cae,
      // sondear /api/me (acelerado) por si la sesion expiro.
      if (Date.now() - lastProbeRef.current > 8000) {
        lastProbeRef.current = Date.now()
        refreshMe()
      }
    }
    // Indicador de conexion: sin eventos por >10 s = telemetria congelada.
    const staleTimer = setInterval(() => {
      setStaleSince(Date.now() - lastEventRef.current > 10_000 ? lastEventRef.current : null)
    }, 3000)
    return () => { clearInterval(staleTimer); es.close(); esRef.current = null }
  }, [auth, refreshJobs, refreshMe, pushToast])

  const rendering = jobs.some((j) => j.status === 'running')

  // El titulo de la pestaña refleja el estado del render (se ve aunque estes
  // en otra pestaña del navegador).
  useEffect(() => {
    document.title = rendering
      ? '● Renderizando… · ManimStudio'
      : 'ManimStudio · coderesearch.space'
  }, [rendering])

  if (auth === null) {
    return <div className="boot">CONECTANDO…</div>
  }
  if (auth === false) {
    return <Login onLogin={refreshMe} />
  }

  const lastFinished = jobs.find((j) => !['queued', 'running'].includes(j.status))
  const orbitState = rendering
    ? 'rendering'
    : lastFinished && ['error', 'timeout'].includes(lastFinished.status)
      ? 'error'
      : 'idle'

  const logout = async () => {
    try { await api.logout() } finally { setAuth(false) }
  }

  // display:contents mantiene al <main> de cada vista como hijo directo del
  // flex del shell; hidden (display:none) lo saca de layout sin desmontarlo.
  const show = (id) => (view === id ? 'contents' : 'hidden')

  return (
    // Shell responsive: en movil la pagina scrollea (min-h) y cada vista fija
    // alturas minimas por panel; en lg+ vuelve el layout de viewport fijo.
    <div className="flex min-h-dvh flex-col lg:h-dvh relative">
      <StarfieldBackground />
      <Header
        view={view}
        onView={navigate}
        metrics={metrics}
        orbitState={orbitState}
        staleSince={staleSince}
        onLogout={logout}
      />
      {/* Avisos de fin de render: visibles desde cualquier vista interna. */}
      <div aria-live="polite" className="fixed bottom-4 right-4 z-50 flex w-[290px] flex-col gap-2">
        {toasts.map(({ key, job }) => {
          const m = TOAST_META[job.status] || TOAST_META.cancelled
          return (
            <div key={key} className="panel flex items-center gap-2.5 px-3 py-2.5 shadow-xl">
              <span className={cn('h-2 w-2 shrink-0 rounded-full', m.dot)} />
              <button onClick={() => { navigate('studio'); dismissToast(key) }}
                className="flex min-w-0 flex-1 flex-col text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
                title="ver en el Estudio">
                <span className="truncate font-mono text-[13px] text-ink">{job.scene}</span>
                <span className={cn('font-mono text-[11px] uppercase tracking-wide', m.text)}>
                  render {m.label}
                </span>
              </button>
              <button aria-label="descartar aviso" onClick={() => dismissToast(key)}
                className="shrink-0 rounded p-1 text-muted transition-colors hover:bg-surface-2 hover:text-ink">
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          )
        })}
      </div>
      {visited.current.has('studio') && (
        <div className={show('studio')}>
          <Studio jobs={jobs} liveLog={liveLog} resetLiveLog={resetLiveLog}
            onJobsChanged={refreshJobs} aiEnabled={aiEnabled}
            pendingScript={pendingScript} onConsumePendingScript={() => setPendingScript(null)} />
        </div>
      )}
      {visited.current.has('library') && (
        <div className={show('library')}>
          <Library jobs={jobs} storage={storage} onJobsChanged={refreshJobs} />
        </div>
      )}
      {visited.current.has('lessons') && (
        <div className={show('lessons')}>
          <Lessons active={view === 'lessons'}
            routeId={view === 'lessons' ? route.param : null}
            onRoute={(id) => navigate('lessons', id)} />
        </div>
      )}
      {visited.current.has('animations') && (
        <div className={show('animations')}>
          <Animations
            routeId={view === 'animations' ? route.param : null}
            onRoute={(id) => navigate('animations', id)}
            onOpenInStudio={(script) => { setPendingScript(script); navigate('studio') }} />
        </div>
      )}
      {visited.current.has('admin') && (
        <div className={show('admin')}>
          <Admin metrics={metrics} containers={containers} jobs={jobs}
            storage={storage} onJobsChanged={refreshJobs}
            routeTab={view === 'admin' ? route.param : null}
            onRoute={(tab) => navigate('admin', tab)} />
        </div>
      )}
    </div>
  )
}
