// Panel de administracion: salud del host, contenedores, gestion de jobs y disco.

import { useEffect, useState } from 'react'
import { api } from './api.js'
import { Chart, useHistory, GB } from './charts.jsx'
import { Button } from './components/ui/button.jsx'
import { cn } from '@/lib/utils'

const MB = 1024 ** 2

function fmtGB(bytes) { return `${(bytes / GB).toFixed(1)} G` }

function fmtSize(bytes) {
  if (bytes == null) return '—'
  if (bytes >= 1024 * MB) return `${(bytes / (1024 * MB)).toFixed(2)} GB`
  if (bytes >= MB) return `${(bytes / MB).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}

function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

const TONE = { crit: 'text-err', warn: 'text-warn', ok: 'text-ok' }

function stateColor(s) {
  if (s === 'running' || s === 'done') return 'text-ok'
  if (s === 'error' || s === 'timeout') return 'text-err'
  if (s === 'restarting' || s === 'paused' || s === 'queued') return 'text-warn'
  return 'text-muted'
}

function PanelHead({ title, aside }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
      <span className="eyebrow">{title}</span>
      {aside != null && <span className="font-mono text-[11px] text-faint">{aside}</span>}
    </div>
  )
}

function StatTile({ label, value, unit, level }) {
  return (
    <div className="rounded-lg border border-line bg-surface-2 px-3.5 py-3">
      <div className="eyebrow">{label}</div>
      <div className={cn('mt-1.5 font-mono text-[26px] font-semibold leading-none', TONE[level] || 'text-ink')}>
        {value}<span className="ml-0.5 text-[13px] font-normal text-muted">{unit}</span>
      </div>
    </div>
  )
}

function Meter({ label, pct, detail, warnAt = 80 }) {
  const tone = pct >= 92 ? 'bg-err' : pct >= warnAt ? 'bg-warn' : 'bg-cyan'
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="eyebrow">{label}</span>
        <span className="font-mono text-xs tabular-nums text-ink">{pct.toFixed(1)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full border border-line bg-canvas"
        role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
        <div className={cn('h-full rounded-full transition-[width] duration-500', tone)}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <p className="mt-1.5 text-[11.5px] text-muted">{detail}</p>
    </div>
  )
}

// Accion destructiva en dos toques: arma y confirma.
function ArmedButton({ label, confirmLabel, onFire }) {
  const [arming, setArming] = useState(false)
  if (arming) {
    return (
      <span className="inline-flex gap-1.5">
        <Button size="xs" variant="danger" onClick={() => { setArming(false); onFire() }}>{confirmLabel}</Button>
        <Button size="xs" variant="ghost" onClick={() => setArming(false)}>No</Button>
      </span>
    )
  }
  return <Button size="xs" variant="danger" onClick={() => setArming(true)}>{label}</Button>
}

const TABS = [
  { id: 'salud', label: 'Salud' },
  { id: 'jobs', label: 'Jobs' },
  { id: 'recursos', label: 'Recursos' },
]

export default function Admin({ metrics, containers, jobs, storage, onJobsChanged,
  routeTab, onRoute }) {
  const samples = useHistory(metrics, containers)
  const now = metrics?.ts || Date.now() / 1000
  const [notice, setNotice] = useState('')
  const isTab = (t) => TABS.some((x) => x.id === t)
  const [tab, setTab] = useState(() => (isTab(routeTab) ? routeTab : 'salud'))

  // #/admin/<tab> (deep-link o atras/adelante) manda sobre el estado local;
  // sin parametro en el hash se conserva la ultima pestana visitada.
  useEffect(() => {
    if (routeTab && routeTab !== tab && isTab(routeTab)) setTab(routeTab)
  }, [routeTab]) // eslint-disable-line react-hooks/exhaustive-deps

  const done = jobs.filter((j) => j.status === 'done')
  const failed = jobs.filter((j) => ['error', 'timeout', 'cancelled'].includes(j.status))
  const active = jobs.filter((j) => ['queued', 'running'].includes(j.status))
  const storagePct = storage?.quota_bytes ? (storage.used_bytes / storage.quota_bytes) * 100 : 0

  const run = async (fn, msg) => {
    setNotice('')
    try {
      const r = await fn()
      setNotice(msg(r))
      onJobsChanged()
    } catch (err) {
      setNotice(`Error: ${err.message}`)
    }
  }

  const clearFailed = () => run(api.deleteFailedJobs, (r) => `${r.deleted} job(s) fallidos eliminados.`)
  const clearHistory = () => run(api.deleteFinishedJobs,
    (r) => `${r.deleted} render(s) borrados · ${fmtSize(r.freed_bytes)} liberados.`)
  const purge = (days) => run(() => api.purgeJobsOlderThan(days),
    (r) => `${r.deleted} render(s) purgados · ${fmtSize(r.freed_bytes)} liberados.`)

  return (
    <main className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <div role="tablist" aria-label="secciones de administración"
        className="flex w-fit flex-wrap gap-1 rounded-lg border border-line bg-canvas/40 p-1">
        {TABS.map((t) => {
          const on = tab === t.id
          return (
            <button key={t.id} role="tab" aria-selected={on}
              onClick={() => { setTab(t.id); onRoute?.(t.id) }}
              className={cn(
                'rounded-md px-3.5 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                on ? 'bg-surface-2 text-accent shadow-sm' : 'text-muted hover:text-ink',
              )}>
              {t.label}
            </button>
          )
        })}
      </div>

      {tab === 'salud' && (
        <>
          <section className="panel" aria-label="salud del sistema">
            <PanelHead title="Salud del sistema"
              aside={metrics ? `load ${metrics.load.join(' / ')} · ${metrics.cpu_count} vCPU` : null} />
            {!metrics ? <p className="p-4 text-[13px] text-muted">Esperando telemetría…</p> : (
              <>
                <div className="grid grid-cols-[repeat(auto-fit,minmax(120px,1fr))] gap-2.5 p-3.5 pb-1">
                  <StatTile label="CPU" value={metrics.cpu_pct.toFixed(0)} unit="%"
                    level={metrics.cpu_pct >= 90 ? 'crit' : metrics.cpu_pct >= 75 ? 'warn' : 'ok'} />
                  <StatTile label="RAM" value={metrics.mem.pct.toFixed(0)} unit="%"
                    level={metrics.mem.pct >= 92 ? 'crit' : metrics.mem.pct >= 80 ? 'warn' : 'ok'} />
                  <StatTile label="Disco /" value={metrics.disk.pct.toFixed(0)} unit="%"
                    level={metrics.disk.pct >= 92 ? 'crit' : metrics.disk.pct >= 80 ? 'warn' : 'ok'} />
                  <StatTile label="Renders" value={String(done.length)} unit=" ok" level="ok" />
                  <StatTile label="Activos" value={String(active.length)} unit="" level={active.length ? 'warn' : 'ok'} />
                </div>
                <div className="grid grid-cols-[repeat(auto-fit,minmax(230px,1fr))] gap-4 p-4">
                  <Meter label="CPU" pct={metrics.cpu_pct} warnAt={75}
                    detail={`${metrics.cpu_count} vCPU compartidas con producción`} />
                  <Meter label="RAM" pct={metrics.mem.pct}
                    detail={`${fmtGB(metrics.mem.used)} / ${fmtGB(metrics.mem.total)} · disp ${fmtGB(metrics.mem.available)}`} />
                  <Meter label="SWAP" pct={metrics.swap.pct} warnAt={40}
                    detail={`${fmtGB(metrics.swap.used)} / ${fmtGB(metrics.swap.total)}`} />
                  <Meter label="Disco /" pct={metrics.disk.pct}
                    detail={`${fmtGB(metrics.disk.used)} / ${fmtGB(metrics.disk.total)} · libres ${fmtGB(metrics.disk.free)}`} />
                </div>
              </>
            )}
          </section>

          <section className="panel" aria-label="gráficas históricas">
            <PanelHead title="Historia · últimos 30 min" aside="banda ámbar = render activo" />
            {samples.length < 2 ? (
              <p className="p-4 text-[13px] text-muted">Acumulando historia… (una muestra cada pocos segundos)</p>
            ) : (
              <div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-4 p-4">
                <Chart title="CPU" field="cpu" color="var(--cyan)" samples={samples} now={now} />
                <Chart title="RAM" field="mem" color="var(--accent)" samples={samples} now={now} />
                <Chart title="Disco /" field="disk" color="var(--ok)" samples={samples} now={now} />
              </div>
            )}
          </section>
        </>
      )}

      {tab === 'jobs' && (
        <section className="panel" aria-label="gestión de jobs">
          <PanelHead title="Gestión de jobs"
            aside={`${done.length} ok · ${failed.length} fallidos · ${active.length} activos · tabla: últimos ${Math.min(25, jobs.length)}`} />
          <div className="flex flex-wrap gap-2 p-3.5 pb-2">
            <ArmedButton label={`Eliminar fallidos (${failed.length})`} confirmLabel="¿Confirmar?" onFire={clearFailed} />
            <ArmedButton label="Purgar renders > 30 días" confirmLabel="¿Confirmar purga?" onFire={() => purge(30)} />
            <ArmedButton label="Purgar renders > 7 días" confirmLabel="¿Confirmar purga?" onFire={() => purge(7)} />
            <ArmedButton label={`Vaciar historial (${done.length + failed.length})`}
              confirmLabel="¿Borrar todo (videos incl.)?" onFire={clearHistory} />
          </div>
          {notice && <p role="status" className="px-3.5 pb-1 text-[12.5px] text-muted">{notice}</p>}
          <div className="overflow-x-auto p-1">
            <table className="w-full border-collapse text-[12.5px]">
              <thead>
                <tr>{['Escena', 'Estado', 'Creado', 'Duración', 'Tamaño'].map((h) => (
                  <th key={h} className="border-b border-line px-3 py-2 text-left font-mono text-[10.5px] font-medium uppercase tracking-[0.14em] text-muted">{h}</th>
                ))}</tr>
              </thead>
              <tbody>
                {jobs.slice(0, 25).map((j) => (
                  <tr key={j.id}>
                    <td className="border-b border-line/40 px-3 py-1.5 font-mono">{j.scene}</td>
                    <td className="border-b border-line/40 px-3 py-1.5">
                      <span className={cn('font-mono text-[11px]', stateColor(j.status))}>{j.status}</span>
                    </td>
                    <td className="border-b border-line/40 px-3 py-1.5">{fmtDate(j.created_at)}</td>
                    <td className="border-b border-line/40 px-3 py-1.5 text-right tabular-nums">
                      {j.started_at && j.finished_at ? `${(j.finished_at - j.started_at).toFixed(0)}s` : '—'}
                    </td>
                    <td className="border-b border-line/40 px-3 py-1.5 text-right font-mono tabular-nums">{fmtSize(j.size_bytes)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {tab === 'recursos' && (
        <>
          <section className="panel" aria-label="almacenamiento">
            <PanelHead title="Almacenamiento · render_jobs/" aside={`${done.length} videos`} />
            {storage && (
              <div className="p-4">
                <Meter label="Cuota" pct={storagePct} warnAt={75}
                  detail={`${fmtSize(storage.used_bytes)} de ${fmtSize(storage.quota_bytes)} · al superar la cuota no se aceptan nuevos renders`} />
              </div>
            )}
          </section>

          <section className="panel" aria-label="contenedores">
            <PanelHead title="Contenedores Docker" aside="solo lectura · sin controles" />
            {containers === null || containers === undefined ? (
              <p className="p-4 text-[13px] text-muted">Telemetría de contenedores no disponible (runner desconectado).</p>
            ) : (
              <div className="overflow-x-auto p-1">
                <table className="w-full border-collapse text-[12.5px]">
                  <thead>
                    <tr>{['Contenedor', 'Estado', 'CPU %', 'MEM %', 'Memoria'].map((h) => (
                      <th key={h} className="border-b border-line px-3 py-2 text-left font-mono text-[10.5px] font-medium uppercase tracking-[0.14em] text-muted">{h}</th>
                    ))}</tr>
                  </thead>
                  <tbody>
                    {containers.map((c) => {
                      const own = c.name === 'codeaerospace-contenido' || c.name.startsWith('manimstudio-render-')
                      return (
                        <tr key={c.name} className={own ? 'bg-accent/[0.06]' : ''}>
                          <td className="border-b border-line/40 px-3 py-1.5 font-mono">
                            {c.name}{own ? ' ◆' : ''}
                          </td>
                          <td className="border-b border-line/40 px-3 py-1.5">
                            <span className={cn('font-mono text-[11px]', stateColor(c.state))}>{c.state}</span>
                          </td>
                          <td className="border-b border-line/40 px-3 py-1.5 text-right tabular-nums">{c.cpu_pct.toFixed(1)}</td>
                          <td className="border-b border-line/40 px-3 py-1.5 text-right tabular-nums">{c.mem_pct.toFixed(1)}</td>
                          <td className="border-b border-line/40 px-3 py-1.5 text-right font-mono tabular-nums">{c.mem_usage || '—'}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
            <p className="border-t border-line px-3 py-3 text-[11.5px] text-muted">
              ◆ contenedores de ManimStudio. El resto pertenece a otros proyectos de este VPS:
              esta consola solo muestra métricas agregadas y no permite ninguna acción sobre ellos.
            </p>
          </section>
        </>
      )}
    </main>
  )
}
