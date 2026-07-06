import { useEffect, useState } from 'react'
import { LogOut, WifiOff } from 'lucide-react'
import ThemePicker from './ThemePicker.jsx'
import { OrbitGlyph } from './components/OrbitGlyph.jsx'
import { Button } from './components/ui/button.jsx'
import { cn } from '@/lib/utils'

const NAV = [
  { id: 'studio', label: 'Estudio' },
  { id: 'library', label: 'Biblioteca' },
  { id: 'lessons', label: 'Aprender' },
  { id: 'animations', label: 'Animaciones' },
  { id: 'admin', label: 'Admin' },
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
    <div className="hidden items-center gap-2 rounded-md border border-line bg-surface-2/50 px-2.5 py-1.5 lg:flex">
      <span className="eyebrow">{label}</span>
      <span className="font-mono text-xs tabular-nums text-ink">{pct.toFixed(0)}%</span>
      <span className="block h-1 w-8 overflow-hidden rounded-full bg-canvas">
        <span className={cn('block h-full rounded-full transition-[width] duration-500', tone)}
          style={{ width: `${Math.min(100, pct)}%` }} />
      </span>
    </div>
  )
}

export default function Header({ view, onView, metrics, orbitState, staleSince, onLogout }) {
  const clock = useUtcClock() // ademas re-renderiza cada segundo: el contador de "sin señal" avanza solo
  return (
    // En movil el header ocupa dos filas: marca + acciones arriba y la nav a
    // lo ancho debajo (order-last + w-full); en md+ vuelve a una sola fila.
    <header className="sticky top-0 z-40 flex shrink-0 flex-wrap items-center gap-x-3 border-b border-line bg-surface/80 px-3 pt-2 backdrop-blur-md md:h-14 md:flex-nowrap md:gap-4 md:px-4 md:pt-0">
      <div className="flex shrink-0 items-center gap-2.5">
        <OrbitGlyph state={orbitState} size={34} />
        <div className="leading-none">
          <div className="font-display text-[15px] font-semibold tracking-tight text-ink">ManimStudio</div>
          <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-faint">Render console</div>
        </div>
      </div>

      <nav aria-label="vistas"
        className="order-last -mx-1 flex w-full items-center gap-1 overflow-x-auto p-1 md:order-none md:mx-0 md:ml-1 md:w-auto md:rounded-lg md:border md:border-line md:bg-canvas/40">
        {NAV.map((n) => {
          const active = view === n.id
          return (
            <button
              key={n.id}
              onClick={() => onView(n.id)}
              aria-current={active ? 'page' : undefined}
              className={cn(
                'shrink-0 rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                active ? 'bg-surface-2 text-accent shadow-sm' : 'text-muted hover:text-ink',
              )}
            >
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
        {metrics && (
          <>
            <MeterChip label="CPU" pct={metrics.cpu_pct} />
            <MeterChip label="RAM" pct={metrics.mem.pct} />
          </>
        )}
        <span className="hidden font-mono text-xs tabular-nums tracking-wide text-muted md:inline">
          {clock} <span className="text-faint">UTC</span>
        </span>
        <ThemePicker />
        <Button variant="ghost" size="sm" onClick={onLogout} title="Cerrar sesión">
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline">Salir</span>
        </Button>
      </div>
    </header>
  )
}
