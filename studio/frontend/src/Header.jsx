import { useEffect, useState } from 'react'
import {
  Activity, FileCode, Film, FlaskConical, FolderKanban, GraduationCap,
  Settings as SettingsIcon, WifiOff, Search,
} from 'lucide-react'
import { OrbitGlyph } from './components/OrbitGlyph.jsx'
import { Wordmark } from './components/Brand.jsx'
import { usePref } from './prefs.js'
import { cn } from '@/lib/utils'

// Una entrada por TAREA, no por endpoint (encargo 7). Proyectos va primero
// porque es donde vive el trabajo real (el catalogo son ~60 cursos); el
// Estudio es su editor. "Renders" era "Biblioteca", nombre que chocaba con la
// biblioteca de contenido de Aprender; y Animaciones dejo de ser seccion
// propia: es la mitad practica de Aprender y comparten indice.
const NAV = [
  { id: 'projects', label: 'Proyectos', icon: FolderKanban },
  { id: 'studio', label: 'Estudio', icon: FileCode },
  { id: 'renders', label: 'Renders', icon: Film },
  { id: 'learn', label: 'Aprender', icon: GraduationCap },
  // El Laboratorio va DESPUES del Estudio en la lectura pero antes de Admin:
  // es trabajo de contenido (verificar la libreria antes de escribir un
  // clip), no salud del host.
  { id: 'lab', label: 'Laboratorio', icon: FlaskConical },
  { id: 'admin', label: 'Admin', icon: Activity },
]

function useUtcClock() {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return now.toISOString().slice(11, 19)
}

function MeterChip({ label, pct }) {
  const tone = pct >= 90 ? 'bg-err' : pct >= 70 ? 'bg-warn' : 'bg-cyan'
  return (
    // 2xl y no lg: la nav crecio a seis vistas (Laboratorio, sprint R3b) y a
    // 1440 px los dos medidores le comian el ultimo boton — "Admin" salia
    // cortado sin que nada lo dijera. La telemetria es informativa y hasta se
    // puede apagar (Configuracion); la navegacion no es opcional, asi que la
    // que cede es la telemetria. Medido con Playwright a 1024/1180/1280/1366/
    // 1440/1600/1920: recorte 0 en todas salvo 1024, donde la nav ya
    // scrolleaba antes de este sprint.
    <div className="hidden items-center gap-2 rounded-md border border-line bg-surface-2/50 px-2.5 py-1.5 2xl:flex">
      <span className="eyebrow">{label}</span>
      <span className="font-mono text-xs tabular-nums text-ink">{pct.toFixed(0)}%</span>
      <span className="block h-1 w-8 overflow-hidden rounded-full bg-canvas">
        <span className={cn('block h-full rounded-full transition-[width] duration-500', tone)}
          style={{ width: `${Math.min(100, pct)}%` }} />
      </span>
    </div>
  )
}

export default function Header({ view, onView, metrics, orbitState, staleSince, onPaleta }) {
  const clock = useUtcClock() // ademas re-renderiza cada segundo: el contador de "sin señal" avanza solo
  const telemetry = usePref('telemetry')
  return (
    // En movil el header ocupa dos filas: marca + acciones arriba y la nav a
    // lo ancho debajo (order-last + w-full); en md+ vuelve a una sola fila.
    <header className="sticky top-0 z-40 flex shrink-0 flex-wrap items-center gap-x-3 border-b border-line bg-surface/80 px-3 pt-2 backdrop-blur-md md:h-14 md:flex-nowrap md:gap-4 md:px-4 md:pt-0">
      {/* Marca: el glifo orbital sigue siendo el estado del render, pero
          debajo del nombre va el wordmark del canal — la consola pertenece a
          CO.DE Academy y eso se ve en todas las vistas, no solo en el login. */}
      <div className="flex shrink-0 items-center gap-2.5">
        <OrbitGlyph state={orbitState} size={34} />
        <div className="leading-none">
          <div className="font-display text-[15px] font-semibold tracking-tight text-ink">ManimStudio</div>
          <Wordmark size="sm" className="mt-1 text-[10px]" />
        </div>
      </div>

      <nav aria-label="vistas"
        className="order-last -mx-1 flex w-full items-center gap-1 overflow-x-auto p-1 md:order-none md:mx-0 md:ml-1 md:w-auto md:rounded-lg md:border md:border-line md:bg-canvas/40">
        {NAV.map((n) => {
          const active = view === n.id
          const Icon = n.icon
          return (
            <button
              key={n.id}
              onClick={() => onView(n.id)}
              aria-current={active ? 'page' : undefined}
              className={cn(
                'flex shrink-0 items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                active ? 'bg-surface-2 text-accent shadow-sm' : 'text-muted hover:text-ink',
              )}
            >
              {Icon && <Icon className="h-3.5 w-3.5" />}
              {n.label}
            </button>
          )
        })}
      </nav>

      <div className="ml-auto flex items-center gap-2">
        {staleSince && (
          <span role="status"
            className="flex items-center gap-1.5 rounded-md border border-warn/40 bg-warn/10 px-2 py-1 font-mono text-[11px] text-warn"
            title="el stream de telemetria no envia eventos; los datos en pantalla estan congelados">
            <WifiOff className="h-3 w-3" />
            <span className="hidden sm:inline">sin señal</span>
            {Math.max(0, Math.floor((Date.now() - staleSince) / 1000))}s
          </span>
        )}
        {/* Telemetria: informativa, no un ajuste — se puede apagar desde
            Configuracion cuando estorba (encargo 5). */}
        {telemetry && metrics && (
          <>
            <MeterChip label="CPU" pct={metrics.cpu_pct} />
            <MeterChip label="RAM" pct={metrics.mem.pct} />
          </>
        )}
        {telemetry && (
          <span className="hidden font-mono text-xs tabular-nums tracking-wide text-muted xl:inline">
            {clock} <span className="text-faint">UTC</span>
          </span>
        )}
        {/* La puerta visible a la paleta de comandos: un atajo que no se ve
            no existe para quien no lee la hoja de atajos. */}
        {onPaleta && (
          <button
            onClick={onPaleta}
            title="Buscar e ir (Ctrl+K)"
            className="hidden h-9 items-center gap-2 rounded-md border border-line px-2.5 text-sm text-muted transition-colors hover:border-line-strong hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan sm:flex">
            <Search className="h-4 w-4" aria-hidden="true" />
            {/* Los rotulos de las dos acciones de la derecha ceden antes que
                la nav (ver MeterChip): por debajo de xl quedan como iconos con
                `title`, que es lo que la cabecera ya hacia por debajo de sm. */}
            <span className="hidden xl:inline">Buscar</span>
            <kbd className="hidden rounded border border-line px-1 py-0.5 font-mono text-[10px] text-faint xl:inline">Ctrl K</kbd>
          </button>
        )}
        {/* La barra ya no lleva ajustes (encargo 8): ni selector de tema ni
            "Salir". Solo la puerta a Configuracion, que es navegacion. */}
        <button
          onClick={() => onView('settings')}
          aria-current={view === 'settings' ? 'page' : undefined}
          title="Configuración"
          className={cn(
            'flex h-9 items-center gap-2 rounded-md border px-2.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
            view === 'settings'
              ? 'border-accent/50 bg-surface-2 text-accent'
              : 'border-line text-muted hover:border-line-strong hover:text-ink',
          )}
        >
          <SettingsIcon className="h-4 w-4" aria-hidden="true" />
          <span className="hidden xl:inline">Configuración</span>
        </button>
      </div>
    </header>
  )
}
