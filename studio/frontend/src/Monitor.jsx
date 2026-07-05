// Centro de monitoreo del VPS: host + contenedores (solo lectura informativa).

const GB = 1024 ** 3

function fmtGB(bytes) {
  return `${(bytes / GB).toFixed(1)} G`
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

export default function Monitor({ metrics, containers }) {
  return (
    <main className="monitor">
      <section className="panel" aria-label="host">
        <div className="panel__bar">
          <span className="panel__title">HOST · coderesearch.space</span>
          {metrics && (
            <span className="panel__aside">
              load {metrics.load.join(' / ')} · {metrics.cpu_count} vCPU
            </span>
          )}
        </div>
        {!metrics ? <p className="empty">Esperando telemetría…</p> : (
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
    </main>
  )
}
