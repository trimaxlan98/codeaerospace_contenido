import { useEffect, useState } from 'react'
import { LogOut } from 'lucide-react'
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

export default function Header({ view, onView, metrics, orbitState, onLogout }) {
  const clock = useUtcClock()
  return (
    <header className="sticky top-0 z-40 flex h-14 shrink-0 items-center gap-4 border-b border-line bg-surface/80 px-4 backdrop-blur-md">
      <div className="flex shrink-0 items-center gap-2.5">
        <OrbitGlyph state={orbitState} size={34} />
        <div className="leading-none">
          <div className="font-display text-[15px] font-semibold tracking-tight text-ink">ManimStudio</div>
          <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-faint">Render console</div>
        </div>
      </div>

      <nav aria-label="vistas"
        className="ml-1 flex items-center gap-1 overflow-x-auto rounded-lg border border-line bg-canvas/40 p-1">
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
