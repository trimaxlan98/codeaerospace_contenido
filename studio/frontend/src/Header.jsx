import { useEffect, useState } from 'react'

function useUtcClock() {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return now.toISOString().slice(11, 19)
}

// Firma visual: el satelite orbita lento en reposo, rapido y ambar mientras
// renderiza, rojo tras un fallo. El estado del sistema ES el ornamento.
export function OrbitGlyph({ state }) {
  return (
    <svg className={`orbit orbit--${state}`} viewBox="0 0 48 48" width="34" height="34"
      role="img" aria-label={`estado: ${state}`}>
      <circle cx="24" cy="24" r="5.5" className="orbit__body" />
      <ellipse cx="24" cy="24" rx="19" ry="8.5" className="orbit__path"
        transform="rotate(-18 24 24)" />
      <g className="orbit__spin">
        <circle cx="43" cy="24" r="2.6" className="orbit__sat"
          transform="rotate(-18 24 24)" />
      </g>
    </svg>
  )
}

export default function Header({ view, onView, metrics, orbitState, onLogout }) {
  const clock = useUtcClock()
  return (
    <header className="hdr">
      <div className="hdr__brand">
        <OrbitGlyph state={orbitState} />
        <span className="hdr__mark">MANIM·STUDIO</span>
      </div>
      <nav className="hdr__nav" aria-label="vistas">
        <button className={view === 'studio' ? 'tab tab--on' : 'tab'}
          onClick={() => onView('studio')}>Estudio</button>
        <button className={view === 'library' ? 'tab tab--on' : 'tab'}
          onClick={() => onView('library')}>Biblioteca</button>
        <button className={view === 'monitor' ? 'tab tab--on' : 'tab'}
          onClick={() => onView('monitor')}>Monitoreo</button>
      </nav>
      <div className="hdr__telemetry">
        {metrics && (
          <>
            <span className="chip">CPU <b>{metrics.cpu_pct.toFixed(0)}%</b></span>
            <span className="chip">RAM <b>{metrics.mem.pct.toFixed(0)}%</b></span>
          </>
        )}
        <span className="chip chip--clock">{clock} UTC</span>
        <button className="btn btn--ghost" onClick={onLogout}>Cerrar sesión</button>
      </div>
    </header>
  )
}
