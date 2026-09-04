import { useCallback, useEffect, useRef, useState } from 'react'
import { X } from 'lucide-react'
import { api, setUnauthorizedHandler } from './api.js'
import { useRoute } from './router.js'
import CommandPalette from './components/CommandPalette.jsx'
import { AtajosDialog, useAtajos } from './components/Atajos.jsx'
import { getPrefs } from './prefs.js'
import { cursoDeJob, useCatalogo } from './catalogo.js'
import { cn } from '@/lib/utils'
import Login from './Login.jsx'
import ChangePassword from './ChangePassword.jsx'
import Header from './Header.jsx'
import Studio from './Studio.jsx'
import Admin from './Admin.jsx'
import Renders from './Renders.jsx'
import Biblioteca from './Biblioteca.jsx'
import Laboratorio from './Laboratorio.jsx'
import Learn from './Learn.jsx'
import Projects from './Projects.jsx'
import Settings from './Settings.jsx'
import StarfieldBackground from './components/StarfieldBackground.jsx'
import { BrandMark } from './components/Brand.jsx'

const TOAST_META = {
  done: { label: 'listo', dot: 'bg-ok', text: 'text-ok' },
  error: { label: 'con error', dot: 'bg-err', text: 'text-err' },
  timeout: { label: 'timeout', dot: 'bg-err', text: 'text-err' },
  cancelled: { label: 'cancelado', dot: 'bg-muted', text: 'text-muted' },
}

export default function App() {
  const [auth, setAuth] = useState(null) // null=cargando, false=no, true=si
  const [mustChangePassword, setMustChangePassword] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(false)
  const [user, setUser] = useState('')
  const [route, navigate] = useRoute()
  // Atajos globales (Ctrl+K, g+tecla, ?) y los dos dialogos que abren.
  const { paleta, setPaleta, ayuda, setAyuda } = useAtajos(navigate)
  const view = route.view
  // Nombres de curso: los avisos de fin de render decian solo la escena
  // (`Clip3`), que con ~300 clips en catalogo no identifica nada.
  const catalogo = useCatalogo(auth === true)
  // Vistas keep-alive: se montan al visitarlas por primera vez y despues solo
  // se ocultan, para que su estado (editor, leccion abierta, tab de Admin…)
  // sobreviva a los cambios de pestana.
  const visited = useRef(new Set())
  visited.current.add(view)
  const [pendingScript, setPendingScript] = useState(null)
  // Escena a preseleccionar junto con pendingScript (viaja solo cuando el
  // origen es un clip de Proyectos; Animaciones no la usa).
  const [pendingScene, setPendingScene] = useState(null)
  // Contexto del clip abierto desde Proyectos para editar en el Estudio.
  const [clipContext, setClipContext] = useState(null)
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
    // Preferencia leida en el momento del aviso (no en el render): apagarla
    // no debe reconstruir el efecto del SSE.
    if (!getPrefs().toasts) return
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
      setUser(d.user || '')
      setMustChangePassword(Boolean(d.must_change_password))
    } catch {
      setAuth(false)
    }
  }, [])

  useEffect(() => { refreshMe() }, [refreshMe]) // consulta inicial al montar

  // Stream SSE unico: metricas + estados de job + logs en vivo.
  useEffect(() => {
    if (auth !== true || mustChangePassword) return
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
  }, [auth, mustChangePassword, refreshJobs, refreshMe, pushToast])

  const rendering = jobs.some((j) => j.status === 'running')

  // El titulo de la pestaña refleja el estado del render (se ve aunque estes
  // en otra pestaña del navegador).
  useEffect(() => {
    document.title = rendering
      ? '● Renderizando… · ManimStudio'
      : 'ManimStudio · CO.DE Academy'
  }, [rendering])

  const logout = async () => {
    try { await api.logout() } finally { setAuth(false); setMustChangePassword(false) }
  }

  if (auth === null) {
    // Arranque: la marca aparece ya en el primer pintado, antes de saber si
    // hay sesion (encargo 11 — la identidad no es solo del video).
    return (
      <div className="boot">
        <BrandMark size={44} />
        <span>CONECTANDO…</span>
      </div>
    )
  }
  if (auth === false) {
    return <Login onLogin={refreshMe} />
  }
  if (mustChangePassword) {
    return <ChangePassword onChanged={refreshMe} onLogout={logout} />
  }

  const lastFinished = jobs.find((j) => !['queued', 'running'].includes(j.status))
  const orbitState = rendering
    ? 'rendering'
    : lastFinished && ['error', 'timeout'].includes(lastFinished.status)
      ? 'error'
      : 'idle'

  // display:contents mantiene al <main> de cada vista como hijo directo del
  // flex del shell; hidden (display:none) lo saca de layout sin desmontarlo.
  // El id viaja con la vista visible: es el destino del "saltar al contenido"
  // y solo una vista lo lleva a la vez (las otras siguen montadas y ocultas).
  const pane = (id) => ({
    className: view === id ? 'contents' : 'hidden',
    id: view === id ? 'contenido' : undefined,
  })

  return (
    // Shell responsive: en movil la pagina scrollea (min-h) y cada vista fija
    // alturas minimas por panel; en lg+ vuelve el layout de viewport fijo.
    <div className="flex min-h-dvh flex-col lg:h-dvh relative">
      <StarfieldBackground />
      {/* Primer tabulador del documento. No puede ser un <a href="#..."> :
          la navegacion es por hash y el ancla cambiaria de vista. */}
      <button
        onClick={() => {
          const el = document.querySelector('#contenido main')
          if (!el) return
          el.tabIndex = -1
          el.focus({ preventScroll: true })
          el.scrollIntoView({ block: 'start' })
        }}
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-md focus:border focus:border-accent focus:bg-surface focus:px-3 focus:py-2 focus:text-[13px] focus:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
        Saltar al contenido
      </button>
      <CommandPalette open={paleta} onOpenChange={setPaleta}
        onNavigate={(v, p) => navigate(v, p)} />
      <AtajosDialog open={ayuda} onOpenChange={setAyuda} />
      <Header
        view={view}
        onView={navigate}
        onPaleta={() => setPaleta(true)}
        metrics={metrics}
        orbitState={orbitState}
        staleSince={staleSince}
      />
      {/* Avisos de fin de render: visibles desde cualquier vista interna. */}
      <div aria-live="polite" className="fixed bottom-4 right-4 z-50 flex w-[290px] flex-col gap-2">
        {toasts.map(({ key, job }) => {
          const m = TOAST_META[job.status] || TOAST_META.cancelled
          const curso = cursoDeJob(job, catalogo)
          return (
            <div key={key} className="panel flex items-center gap-2.5 px-3 py-2.5 shadow-xl">
              <span className={cn('h-2 w-2 shrink-0 rounded-full', m.dot)} />
              {/* El aviso lleva al sitio donde se sigue trabajando: al curso
                  si el render es un clip, al Estudio si es un render libre. */}
              <button onClick={() => {
                if (curso) navigate('projects', curso.id); else navigate('studio')
                dismissToast(key)
              }}
                className="flex min-w-0 flex-1 flex-col text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
                title={curso ? `ver ${curso.name}` : 'ver en el Estudio'}>
                <span className="truncate font-mono text-[13px] text-ink">{job.scene}</span>
                {curso && (
                  <span className="truncate text-[11.5px] text-muted">{curso.label}</span>
                )}
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
        <div {...pane('studio')}>
          <Studio jobs={jobs} liveLog={liveLog} resetLiveLog={resetLiveLog}
            onJobsChanged={refreshJobs} aiEnabled={aiEnabled}
            pendingScript={pendingScript} pendingScene={pendingScene}
            onConsumePendingScript={() => { setPendingScript(null); setPendingScene(null) }}
            clipContext={clipContext} onExitClip={() => setClipContext(null)}
            onOpenProject={(id) => navigate('projects', id)} />
        </div>
      )}
      {visited.current.has('projects') && (
        <div {...pane('projects')}>
          <Projects jobs={jobs} aiEnabled={aiEnabled}
            routeId={view === 'projects' ? route.param : null}
            onRoute={(id) => navigate('projects', id)}
            onEditClip={(ctx, script, scene) => {
              setPendingScript(script)
              setPendingScene(scene)
              setClipContext(ctx)
              navigate('studio')
            }} />
        </div>
      )}
      {visited.current.has('renders') && (
        <div {...pane('renders')}>
          <Renders jobs={jobs} storage={storage} onJobsChanged={refreshJobs}
            onOpenProject={(id) => navigate('projects', id)} />
        </div>
      )}
      {visited.current.has('learn') && (
        <div {...pane('learn')}>
          <Learn active={view === 'learn'}
            routeId={view === 'learn' ? route.param : null}
            onRoute={(id) => navigate('learn', id)}
            onOpenInStudio={(script) => { setPendingScript(script); navigate('studio') }}
            onOpenProject={(id) => navigate('projects', id)} />
        </div>
      )}
      {visited.current.has('entregas') && (
        <div {...pane('entregas')}>
          <Biblioteca active={view === 'entregas'} />
        </div>
      )}
      {visited.current.has('lab') && (
        <div {...pane('lab')}>
          <Laboratorio active={view === 'lab'} />
        </div>
      )}
      {visited.current.has('admin') && (
        <div {...pane('admin')}>
          <Admin metrics={metrics} containers={containers} jobs={jobs}
            storage={storage} onJobsChanged={refreshJobs}
            routeTab={view === 'admin' ? route.param : null}
            onRoute={(tab) => navigate('admin', tab)} />
        </div>
      )}
      {visited.current.has('settings') && (
        <div {...pane('settings')}>
          <Settings user={user} aiEnabled={aiEnabled} onLogout={logout} />
        </div>
      )}
    </div>
  )
}
