// Biblioteca: videos renderizados (grid de tarjetas) + gestión de disco.

import { useEffect, useState } from 'react'
import { api, thumbUrl, videoUrl } from './api.js'

const MB = 1024 ** 2

function fmtSize(bytes) {
  if (bytes == null) return '—'
  if (bytes >= 1024 * MB) return `${(bytes / (1024 * MB)).toFixed(2)} GB`
  return `${(bytes / MB).toFixed(1)} MB`
}

function fmtDate(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

function duration(job) {
  if (!job.started_at || !job.finished_at) return null
  return `${(job.finished_at - job.started_at).toFixed(0)}s`
}

const QUALITY_LABEL = { ql: '480p', qm: '720p', qh: '1080p' }
const STATUS_LABEL = {
  error: 'error', cancelled: 'cancelado', timeout: 'timeout',
}

function DeleteButton({ onDelete }) {
  const [arming, setArming] = useState(false)
  useEffect(() => {
    if (!arming) return
    const t = setTimeout(() => setArming(false), 3500)
    return () => clearTimeout(t)
  }, [arming])
  return arming ? (
    <button className="btn btn--tiny btn--danger" onClick={onDelete}>¿Confirmar borrado?</button>
  ) : (
    <button className="btn btn--tiny" onClick={() => setArming(true)}>Borrar</button>
  )
}

function StorageBar({ storage }) {
  if (!storage) return null
  const pct = storage.quota_bytes ? (storage.used_bytes / storage.quota_bytes) * 100 : 0
  const level = pct >= 92 ? 'crit' : pct >= 75 ? 'warn' : 'ok'
  return (
    <div className="meter meter--storage">
      <div className="meter__head">
        <span className="meter__label">ALMACENAMIENTO · render_jobs/</span>
        <span className="meter__val">{pct.toFixed(1)}%</span>
      </div>
      <div className="meter__track" role="progressbar" aria-valuenow={Math.round(pct)}
        aria-valuemin="0" aria-valuemax="100" aria-label="uso de disco de renders">
        <div className={`meter__fill meter__fill--${level}`}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <span className="meter__detail">
        {fmtSize(storage.used_bytes)} de {fmtSize(storage.quota_bytes)} · al superar la
        cuota no se aceptan nuevos renders
      </span>
    </div>
  )
}

export default function Library({ jobs, storage, onJobsChanged }) {
  const [playing, setPlaying] = useState(null) // job en el visor
  const [error, setError] = useState('')

  const videos = jobs.filter((j) => j.status === 'done')
  const failed = jobs.filter((j) => ['error', 'timeout', 'cancelled'].includes(j.status))

  const remove = async (id) => {
    setError('')
    try {
      await api.deleteJob(id)
      if (playing?.id === id) setPlaying(null)
      onJobsChanged()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="library">
      <section className="panel" aria-label="uso de disco">
        <div className="panel__bar">
          <span className="panel__title">BIBLIOTECA</span>
          <span className="panel__aside">{videos.length} video{videos.length === 1 ? '' : 's'}</span>
        </div>
        <div className="library__storage">
          <StorageBar storage={storage} />
        </div>
        {error && <p className="notice notice--warn" role="alert">{error}</p>}
      </section>

      <section className="panel panel--grid" aria-label="videos renderizados">
        {videos.length === 0 ? (
          <p className="empty">Sin videos todavía. Los renders exitosos aparecen aquí.</p>
        ) : (
          <div className="cards">
            {videos.map((j) => (
              <article key={j.id} className="card">
                <button className="card__thumb" onClick={() => setPlaying(j)}
                  aria-label={`ver ${j.scene}`}>
                  {j.has_thumb
                    ? <img src={thumbUrl(j.id)} alt={`miniatura de ${j.scene}`} loading="lazy" />
                    : <span className="card__noimg">▶</span>}
                  <span className="card__play" aria-hidden="true">▶</span>
                </button>
                <div className="card__body">
                  <h3 className="card__title" title={j.scene}>{j.scene}</h3>
                  <p className="card__meta">
                    {fmtDate(j.created_at)} · {duration(j) || '—'} ·{' '}
                    {QUALITY_LABEL[j.quality] || j.quality} · {fmtSize(j.size_bytes)}
                  </p>
                  <div className="card__actions">
                    <button className="btn btn--tiny" onClick={() => setPlaying(j)}>Ver</button>
                    <a className="btn btn--tiny" href={videoUrl(j.id)}
                      download={`${j.scene}.mp4`}>Descargar</a>
                    <DeleteButton onDelete={() => remove(j.id)} />
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {failed.length > 0 && (
        <section className="panel" aria-label="historial de fallos">
          <div className="panel__bar">
            <span className="panel__title">FALLIDOS / CANCELADOS</span>
            <span className="panel__aside">sin video · solo registro</span>
          </div>
          <ul className="jobs">
            {failed.map((j) => (
              <li key={j.id} className="job">
                <span className={`dot dot--${j.status}`} aria-hidden="true" />
                <span className="job__scene">{j.scene}</span>
                <span className="job__meta">{fmtDate(j.created_at)}</span>
                <span className={`job__status job__status--${j.status}`}>
                  {STATUS_LABEL[j.status] || j.status}
                </span>
                <DeleteButton onDelete={() => remove(j.id)} />
              </li>
            ))}
          </ul>
        </section>
      )}

      {playing && (
        <div className="lightbox" role="dialog" aria-label={`video ${playing.scene}`}
          onClick={() => setPlaying(null)}>
          <div className="lightbox__box" onClick={(e) => e.stopPropagation()}>
            <div className="panel__bar">
              <span className="panel__title">{playing.scene} · {playing.id.slice(0, 8)}</span>
              <button className="btn btn--tiny" onClick={() => setPlaying(null)}>Cerrar ✕</button>
            </div>
            <video className="lightbox__video" controls autoPlay
              src={videoUrl(playing.id)} />
          </div>
        </div>
      )}
    </main>
  )
}
