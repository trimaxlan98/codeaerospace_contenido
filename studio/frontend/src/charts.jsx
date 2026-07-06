// Graficas historicas: SVG dibujado a mano (cero dependencias de charting).

import { useEffect, useRef, useState } from 'react'
import { api } from './api.js'

export const GB = 1024 ** 3
const WINDOW_S = 1800 // 30 min
const W = 600
const H = 220
const PAD = { l: 30, r: 6, t: 10, b: 18 }

function scaleX(ts, now) {
  const x0 = now - WINDOW_S
  return PAD.l + ((ts - x0) / WINDOW_S) * (W - PAD.l - PAD.r)
}

function scaleY(pct) {
  const v = Math.max(0, Math.min(100, pct))
  return PAD.t + (1 - v / 100) * (H - PAD.t - PAD.b)
}

// Tramos contiguos con render activo -> bandas sombreadas.
function renderBands(samples, now) {
  const bands = []
  let start = null
  for (const s of samples) {
    if (s.render && start === null) start = s.ts
    if (!s.render && start !== null) { bands.push([start, s.ts]); start = null }
  }
  if (start !== null) bands.push([start, now])
  return bands.map(([a, b]) => ({
    x: scaleX(a, now),
    w: Math.max(1.5, scaleX(b, now) - scaleX(a, now)),
  }))
}

export function Chart({ title, samples, field, color, now }) {
  const visible = samples.filter((s) => s.ts >= now - WINDOW_S && s[field] != null)
  const coords = visible.map((s) => [scaleX(s.ts, now), scaleY(s[field])])
  const points = coords.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ')
  const baseY = scaleY(0)
  const area = coords.length > 1
    ? `${coords[0][0].toFixed(1)},${baseY} ${points} ${coords[coords.length - 1][0].toFixed(1)},${baseY}`
    : ''
  const last = visible.length ? visible[visible.length - 1][field] : null
  const bands = renderBands(samples.filter((s) => s.ts >= now - WINDOW_S), now)
  const gid = `chartgrad-${field}`
  const fmtT = (ts) => new Date(ts * 1000).toLocaleTimeString('es',
    { hour: '2-digit', minute: '2-digit', hour12: false })

  return (
    <figure className="m-0 flex flex-col gap-2">
      <figcaption className="flex items-center justify-between">
        <span className="eyebrow">{title}</span>
        <span className="font-mono text-[13px] tabular-nums" style={{ color }}>
          {last == null ? '—' : `${last.toFixed(1)}%`}
        </span>
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img"
        className="block w-full rounded-md border border-line bg-canvas"
        aria-label={`serie temporal de ${title}, ultimo valor ${last == null ? 'sin datos' : `${last.toFixed(0)}%`}`}>
        <defs>
          <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.28" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        {bands.map((b, i) => (
          <rect key={i} x={b.x} y={PAD.t} width={b.w} height={H - PAD.t - PAD.b}
            fill="var(--accent)" opacity="0.12" />
        ))}
        {[0, 25, 50, 75, 100].map((v) => (
          <g key={v}>
            <line x1={PAD.l} x2={W - PAD.r} y1={scaleY(v)} y2={scaleY(v)}
              stroke="var(--line)" strokeWidth="0.6" opacity="0.7" />
            {(v === 0 || v === 50 || v === 100) && (
              <text x={PAD.l - 5} y={scaleY(v) + 3} textAnchor="end"
                fill="var(--muted)" fontSize="8.5" fontFamily="var(--font-mono)">{v}</text>
            )}
          </g>
        ))}
        {coords.length > 1 && <polygon points={area} fill={`url(#${gid})`} />}
        {coords.length > 1 && (
          <polyline points={points} fill="none" stroke={color}
            strokeWidth="1.6" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
        )}
        <text x={PAD.l} y={H - 3} fill="var(--muted)" fontSize="8.5"
          fontFamily="var(--font-mono)">{fmtT(now - WINDOW_S)}</text>
        <text x={W - PAD.r} y={H - 3} textAnchor="end" fill="var(--muted)"
          fontSize="8.5" fontFamily="var(--font-mono)">{fmtT(now)}</text>
      </svg>
    </figure>
  )
}

// Historia: snapshot HTTP al montar + muestras en vivo derivadas del SSE.
export function useHistory(metrics, containers) {
  const [samples, setSamples] = useState([])
  const lastTs = useRef(0)

  useEffect(() => {
    let alive = true
    api.metricsHistory()
      .then((d) => {
        if (!alive) return
        setSamples(d.samples)
        lastTs.current = d.samples.length ? d.samples[d.samples.length - 1].ts : 0
      })
      .catch(() => {})
    return () => { alive = false }
  }, [])

  useEffect(() => {
    if (!metrics || metrics.ts <= lastTs.current) return
    lastTs.current = metrics.ts
    const render = Boolean(containers?.some(
      (c) => c.name?.startsWith('manimstudio-render-') && c.state === 'running'))
    setSamples((prev) => [
      ...prev.slice(-899),
      { ts: metrics.ts, cpu: metrics.cpu_pct, mem: metrics.mem.pct,
        disk: metrics.disk.pct, render },
    ])
  }, [metrics, containers])

  return samples
}
