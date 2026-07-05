// Graficas historicas: SVG dibujado a mano (cero dependencias de charting).

import { useEffect, useRef, useState } from 'react'
import { api } from './api.js'

export const GB = 1024 ** 3
const WINDOW_S = 1800 // 30 min
const W = 600
const H = 130
const PAD = { l: 30, r: 6, t: 8, b: 16 }

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
  const points = visible
    .map((s) => `${scaleX(s.ts, now).toFixed(1)},${scaleY(s[field]).toFixed(1)}`)
    .join(' ')
  const last = visible.length ? visible[visible.length - 1][field] : null
  const bands = renderBands(samples.filter((s) => s.ts >= now - WINDOW_S), now)
  const fmtT = (ts) => new Date(ts * 1000).toLocaleTimeString('es',
    { hour: '2-digit', minute: '2-digit', hour12: false })

  return (
    <figure className="chart">
      <figcaption className="chart__head">
        <span className="chart__title">{title}</span>
        <span className="chart__val" style={{ color }}>
          {last == null ? '—' : `${last.toFixed(1)}%`}
        </span>
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} className="chart__svg" role="img"
        aria-label={`serie temporal de ${title}, ultimo valor ${last == null ? 'sin datos' : `${last.toFixed(0)}%`}`}>
        {bands.map((b, i) => (
          <rect key={i} x={b.x} y={PAD.t} width={b.w} height={H - PAD.t - PAD.b}
            className="chart__band" />
        ))}
        {[0, 25, 50, 75, 100].map((v) => (
          <g key={v}>
            <line x1={PAD.l} x2={W - PAD.r} y1={scaleY(v)} y2={scaleY(v)}
              className="chart__grid" />
            {(v === 0 || v === 50 || v === 100) && (
              <text x={PAD.l - 5} y={scaleY(v) + 3} className="chart__tick"
                textAnchor="end">{v}</text>
            )}
          </g>
        ))}
        {visible.length > 1 && (
          <polyline points={points} fill="none" stroke={color}
            strokeWidth="1.6" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
        )}
        <text x={PAD.l} y={H - 3} className="chart__tick">{fmtT(now - WINDOW_S)}</text>
        <text x={W - PAD.r} y={H - 3} className="chart__tick" textAnchor="end">{fmtT(now)}</text>
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
