// Panel de administracion: salud del host, contenedores, gestion de jobs y disco.

import { useState } from 'react'
import { api } from './api.js'
import { Chart, useHistory, GB } from './charts.jsx'

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

function Kpi({ label, value, unit, level }) {
  return (
    <div className={`kpi${level ? ` kpi--${level}` : ''}`}>
      <span className="kpi__label">{label}</span>
      <span className="kpi__value">{value}<small>{unit}</small></span>
    </div>
  )
}

function ArmedButton({ label, confirmLabel, onFire, danger }) {
  const [arming, setArming] = useState(false)
  if (arming) {
    return (
      <span className="armed">
        <button className="btn btn--tiny btn--danger"
          onClick={() => { setArming(false); onFire() }}>{confirmLabel}</button>
        <button className="btn btn--tiny" onClick={() => setArming(false)}>No</button>
      </span>
    )
  }
  return (
    <button className={`btn btn--tiny${danger ? ' btn--danger' : ''}`}
      onClick={() => setArming(true)}>{label}</button>
  )
}

function Bar({ label, pct, detail, warnAt = 80 }) {
  const level = pct >= 92 ? 'crit' : pct >= warnAt ? 'warn' : 'ok'
  return (
    <div className="meter">
      <div className="meter__head">
        <span className="meter__label">{label}</span>
        <span className="meter__val">{pct.toFixed(1)}%</span>
      </div>
      <div className="meter__track" role="progressbar" aria-valuenow={Math.round(pct)}
        aria-valuemin="0" aria-valuemax="100" aria-label={label}>
        <div className={`meter__fill meter__fill--${level}`}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <span className="meter__detail">{detail}</span>
    </div>
  )
}

export default function Admin({ metrics, containers, jobs, storage, onJobsChanged }) {
  const samples = useHistory(metrics, containers)
  const now = metrics?.ts || Date.now() / 1000
  const [notice, setNotice] = useState('')
  const [tab, setTab] = useState('salud')

  const done = jobs.filter((j) => j.status === 'done')
  const failed = jobs.filter((j) => ['error', 'timeout', 'cancelled'].includes(j.status))
  const active = jobs.filter((j) => ['queued', 'running'].includes(j.status))
  const storagePct = storage?.quota_bytes
    ? (storage.used_bytes / storage.quota_bytes) * 100 : 0

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

  const clearFailed = () => run(api.deleteFailedJobs,
    (r) => `${r.deleted} job(s) fallidos eliminados.`)
  const purge = (days) => run(() => api.purgeJobsOlderThan(days),
    (r) => `${r.deleted} render(s) purgados · ${fmtSize(r.freed_bytes)} liberados.`)

  return (
    <main className="monitor admin">
      <div className="seg admin__tabs" role="tablist" aria-label="secciones de administracion">
        {[
          { id: 'salud', label: 'Salud' },
          { id: 'jobs', label: 'Jobs' },
          { id: 'recursos', label: 'Recursos' },
        ].map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id}
            className={tab === t.id ? 'seg__opt seg__opt--on' : 'seg__opt'}
            onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </div>

      {tab === 'salud' && (
        <>
      <section className="panel" aria-label="salud del sistema">
        <div className="panel__bar">
          <span className="panel__title">SALUD DEL SISTEMA</span>
          {metrics && (
            <span className="panel__aside">
              load {metrics.load.join(' / ')} · {metrics.cpu_count} vCPU
            </span>
          )}
        </div>
        {!metrics ? <p className="empty">Esperando telemetría…</p> : (
          <>
            <div className="kpis">
              <Kpi label="CPU" value={metrics.cpu_pct.toFixed(0)} unit="%"
                level={metrics.cpu_pct >= 90 ? 'crit' : metrics.cpu_pct >= 75 ? 'warn' : 'ok'} />
              <Kpi label="RAM" value={metrics.mem.pct.toFixed(0)} unit="%"
                level={metrics.mem.pct >= 92 ? 'crit' : metrics.mem.pct >= 80 ? 'warn' : 'ok'} />
              <Kpi label="DISCO /" value={metrics.disk.pct.toFixed(0)} unit="%"
                level={metrics.disk.pct >= 92 ? 'crit' : metrics.disk.pct >= 80 ? 'warn' : 'ok'} />
              <Kpi label="RENDERS" value={String(done.length)} unit=" ok" level="ok" />
              <Kpi label="ACTIVOS" value={String(active.length)} unit=""
                level={active.length ? 'warn' : 'ok'} />
            </div>
            <div className="meters">
              <Bar label="CPU" pct={metrics.cpu_pct} warnAt={75}
                detail={`${metrics.cpu_count} vCPU compartidas con producción`} />
              <Bar label="RAM" pct={metrics.mem.pct}
                detail={`${fmtGB(metrics.mem.used)} / ${fmtGB(metrics.mem.total)} · disp ${fmtGB(metrics.mem.available)}`} />
              <Bar label="SWAP" pct={metrics.swap.pct} warnAt={40}
                detail={`${fmtGB(metrics.swap.used)} / ${fmtGB(metrics.swap.total)}`} />
              <Bar label="DISCO /" pct={metrics.disk.pct}
                detail={`${fmtGB(metrics.disk.used)} / ${fmtGB(metrics.disk.total)} · libres ${fmtGB(metrics.disk.free)}`} />
            </div>
          </>
        )}
      </section>

      <section className="panel" aria-label="graficas historicas">
        <div className="panel__bar">
          <span className="panel__title">HISTORIA · ÚLTIMOS 30 MIN</span>
          <span className="panel__aside">
            <span className="chart__legendband" aria-hidden="true" /> render activo
          </span>
        </div>
        {samples.length < 2 ? (
          <p className="empty">Acumulando historia… (una muestra cada pocos segundos)</p>
        ) : (
          <div className="charts">
            <Chart title="CPU" field="cpu" color="var(--cyan)" samples={samples} now={now} />
            <Chart title="RAM" field="mem" color="var(--gold)" samples={samples} now={now} />
            <Chart title="DISCO /" field="disk" color="var(--ok)" samples={samples} now={now} />
          </div>
        )}
      </section>
        </>
      )}

      {tab === 'jobs' && (
      <section className="panel" aria-label="gestion de jobs">
        <div className="panel__bar">
          <span className="panel__title">GESTIÓN DE JOBS</span>
          <span className="panel__aside">
            {done.length} ok · {failed.length} fallidos · {active.length} activos
          </span>
        </div>
        <div className="admin__actions">
          <ArmedButton danger label={`Eliminar fallidos (${failed.length})`}
            confirmLabel="¿Confirmar?" onFire={clearFailed} />
          <ArmedButton danger label="Purgar renders > 30 días"
            confirmLabel="¿Confirmar purga?" onFire={() => purge(30)} />
          <ArmedButton danger label="Purgar renders > 7 días"
            confirmLabel="¿Confirmar purga?" onFire={() => purge(7)} />
        </div>
        {notice && <p className="notice" role="status">{notice}</p>}
        <div className="tablewrap">
          <table className="ctable">
            <thead>
              <tr><th>Escena</th><th>Estado</th><th>Creado</th><th>Duración</th><th>Tamaño</th></tr>
            </thead>
            <tbody>
              {jobs.slice(0, 25).map((j) => (
                <tr key={j.id}>
                  <td className="mono">{j.scene}</td>
                  <td><span className={`state state--${j.status}`}>{j.status}</span></td>
                  <td>{fmtDate(j.created_at)}</td>
                  <td className="num">
                    {j.started_at && j.finished_at
                      ? `${(j.finished_at - j.started_at).toFixed(0)}s` : '—'}
                  </td>
                  <td className="mono num">{fmtSize(j.size_bytes)}</td>
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
        <div className="panel__bar">
          <span className="panel__title">ALMACENAMIENTO · render_jobs/</span>
          <span className="panel__aside">{done.length} videos</span>
        </div>
        {storage && (
          <Bar label="CUOTA" pct={storagePct} warnAt={75}
            detail={`${fmtSize(storage.used_bytes)} de ${fmtSize(storage.quota_bytes)} · al superar la cuota no se aceptan nuevos renders`} />
        )}
      </section>

      <section className="panel" aria-label="contenedores">
        <div className="panel__bar">
          <span className="panel__title">CONTENEDORES DOCKER</span>
          <span className="panel__aside">solo lectura · sin controles</span>
        </div>
        {containers === null || containers === undefined ? (
          <p className="empty">Telemetría de contenedores no disponible (runner desconectado).</p>
        ) : (
          <div className="tablewrap">
            <table className="ctable">
              <thead>
                <tr><th>Contenedor</th><th>Estado</th><th>CPU %</th><th>MEM %</th><th>Memoria</th></tr>
              </thead>
              <tbody>
                {containers.map((c) => {
                  const own = c.name === 'codeaerospace-contenido'
                    || c.name.startsWith('manimstudio-render-')
                  return (
                    <tr key={c.name} className={own ? 'ctable__own' : ''}>
                      <td className="mono">{c.name}{own ? ' ◆' : ''}</td>
                      <td><span className={`state state--${c.state}`}>{c.state}</span></td>
                      <td className="num">{c.cpu_pct.toFixed(1)}</td>
                      <td className="num">{c.mem_pct.toFixed(1)}</td>
                      <td className="mono num">{c.mem_usage || '—'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
        <p className="finePrint">
          ◆ contenedores de ManimStudio. El resto pertenece a otros proyectos de este VPS:
          esta consola solo muestra métricas agregadas y no permite ninguna acción sobre ellos.
        </p>
      </section>
        </>
      )}
    </main>
  )
}
