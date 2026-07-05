import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api.js'
import Login from './Login.jsx'
import Header from './Header.jsx'
import Studio from './Studio.jsx'
import Monitor from './Monitor.jsx'

export default function App() {
  const [auth, setAuth] = useState(null) // null=cargando, false=no, true=si
  const [view, setView] = useState('studio')
  const [metrics, setMetrics] = useState(null)
  const [containers, setContainers] = useState(null)
  const [jobs, setJobs] = useState([])
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
    } catch { /* la sesion pudo expirar; lo detecta el proximo request */ }
  }, [])

  useEffect(() => {
    api.me().then((d) => setAuth(d.authenticated)).catch(() => setAuth(false))
  }, [])

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
    return <Login onLogin={() => setAuth(true)} />
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

  return (
    <div className="shell">
      <Header
        view={view}
        onView={setView}
        metrics={metrics}
        orbitState={orbitState}
        onLogout={logout}
      />
      {view === 'studio' ? (
        <Studio jobs={jobs} liveLog={liveLog} resetLiveLog={resetLiveLog}
          onJobsChanged={refreshJobs} />
      ) : (
        <Monitor metrics={metrics} containers={containers} />
      )}
    </div>
  )
}
