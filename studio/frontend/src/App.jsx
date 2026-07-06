import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api.js'
import { useRoute } from './router.js'
import Login from './Login.jsx'
import Header from './Header.jsx'
import Studio from './Studio.jsx'
import Admin from './Admin.jsx'
import Library from './Library.jsx'
import Lessons from './Lessons.jsx'
import Animations from './Animations.jsx'

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
  const esRef = useRef(null)

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
    const es = new EventSource('/api/events')
    esRef.current = es
    es.onmessage = (msg) => {
      const ev = JSON.parse(msg.data)
      if (ev.type === 'metrics') {
        if (ev.host) setMetrics(ev.host)
        if (ev.containers !== undefined) setContainers(ev.containers)
      } else if (ev.type === 'job') {
        setJobs((prev) => {
          const rest = prev.filter((j) => j.id !== ev.job.id)
          return [ev.job, ...rest].sort((a, b) => b.created_at - a.created_at)
        })
        // Al terminar un job cambia el uso de disco: refrescar cuota.
        if (!['queued', 'running'].includes(ev.job.status)) refreshJobs()
      } else if (ev.type === 'joblog') {
        setLiveLog((prev) =>
          prev.jobId === ev.job_id
            ? { jobId: ev.job_id, lines: [...prev.lines.slice(-4999), ev.line] }
            : { jobId: ev.job_id, lines: [ev.line] },
        )
      }
    }
    es.onerror = () => { /* EventSource reintenta solo */ }
    return () => { es.close(); esRef.current = null }
  }, [auth, refreshJobs])

  if (auth === null) {
    return <div className="boot">CONECTANDO…</div>
  }
  if (auth === false) {
    return <Login onLogin={refreshMe} />
  }

  const rendering = jobs.some((j) => j.status === 'running')
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
    <div className="shell">
      <Header
        view={view}
        onView={navigate}
        metrics={metrics}
        orbitState={orbitState}
        onLogout={logout}
      />
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
