// Biblioteca: videos renderizados (grid de tarjetas) + gestión de disco.

import { useEffect, useState } from 'react'
import { Play, Download } from 'lucide-react'
import { api, thumbUrl, videoUrl } from './api.js'
import { Button } from './components/ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'
import { cn } from '@/lib/utils'

const MB = 1024 ** 2

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

function duration(job) {
  if (!job.started_at || !job.finished_at) return null
  return `${(job.finished_at - job.started_at).toFixed(0)}s`
}

const QUALITY_LABEL = { ql: '480p', qm: '720p', qh: '1080p' }
const FAIL_META = {
  error: { label: 'error', dot: 'bg-err', text: 'text-err' },
  timeout: { label: 'timeout', dot: 'bg-err', text: 'text-err' },
  cancelled: { label: 'cancelado', dot: 'bg-muted', text: 'text-muted' },
}

// Borrado en dos toques: el primero arma, el segundo confirma (se desarma solo).
function DeleteButton({ onDelete }) {
  const [arming, setArming] = useState(false)
  useEffect(() => {
    if (!arming) return
    const t = setTimeout(() => setArming(false), 3500)
    return () => clearTimeout(t)
  }, [arming])
  return arming ? (
    <Button size="xs" variant="danger" onClick={onDelete}>¿Confirmar?</Button>
  ) : (
    <Button size="xs" variant="ghost" onClick={() => setArming(true)}>Borrar</Button>
  )
}

function StorageBar({ storage }) {
  if (!storage) return null
  const pct = storage.quota_bytes ? (storage.used_bytes / storage.quota_bytes) * 100 : 0
  const tone = pct >= 92 ? 'bg-err' : pct >= 75 ? 'bg-warn' : 'bg-cyan'
  return (
    <div className="max-w-xl">
      <div className="mb-1.5 flex items-center justify-between">
        <span className="eyebrow">Almacenamiento · render_jobs/</span>
        <span className="font-mono text-xs tabular-nums text-ink">{pct.toFixed(1)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full border border-line bg-canvas"
        role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}
        aria-label="uso de disco de renders">
        <div className={cn('h-full rounded-full transition-[width] duration-500', tone)}
          style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <p className="mt-1.5 text-[11.5px] text-muted">
        {fmtSize(storage.used_bytes)} de {fmtSize(storage.quota_bytes)} · al superar la cuota
        no se aceptan nuevos renders
      </p>
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
    <main className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel" aria-label="uso de disco">
        <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Biblioteca</span>
          <span className="font-mono text-[11px] text-faint">
            {videos.length} video{videos.length === 1 ? '' : 's'}
          </span>
        </div>
        <div className="p-4">
          <StorageBar storage={storage} />
        </div>
        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      <section className="panel" aria-label="videos renderizados">
        {videos.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">Sin videos todavía. Los renders exitosos aparecen aquí.</p>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-3.5 p-4">
            {videos.map((j) => (
              <article key={j.id} className="group flex flex-col overflow-hidden rounded-lg border border-line bg-surface-2 transition-colors hover:border-line-strong">
                <button onClick={() => setPlaying(j)} aria-label={`ver ${j.scene}`}
                  className="relative block aspect-video w-full border-b border-line bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                  {j.has_thumb
                    ? <img src={thumbUrl(j.id)} alt={`miniatura de ${j.scene}`} loading="lazy"
                        className="h-full w-full object-cover" />
                    : <span className="grid h-full place-items-center text-faint"><Play className="h-7 w-7" /></span>}
                  <span className="absolute inset-0 grid place-items-center bg-canvas/45 text-accent opacity-0 transition-opacity group-hover:opacity-100">
                    <Play className="h-9 w-9" fill="currentColor" />
                  </span>
                </button>
                <div className="flex flex-col gap-1.5 p-3">
                  <h3 className="truncate font-mono text-[13px] font-semibold text-ink" title={j.scene}>{j.scene}</h3>
                  <p className="text-[11.5px] text-muted">
                    {fmtDate(j.created_at)} · {duration(j) || '—'} · {QUALITY_LABEL[j.quality] || j.quality} · {fmtSize(j.size_bytes)}
                  </p>
                  <div className="mt-1 flex flex-wrap gap-1.5">
                    <Button size="xs" variant="default" onClick={() => setPlaying(j)}>Ver</Button>
                    <Button size="xs" variant="default" asChild>
                      <a href={videoUrl(j.id)} download={`${j.scene}.mp4`}>
                        <Download className="h-3.5 w-3.5" /> Descargar
                      </a>
                    </Button>
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
          <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
            <span className="eyebrow">Fallidos / cancelados</span>
            <span className="font-mono text-[11px] text-faint">sin video · solo registro</span>
          </div>
          <ul className="divide-y divide-line/40">
            {failed.map((j) => {
              const m = FAIL_META[j.status] || FAIL_META.error
              return (
                <li key={j.id} className="flex flex-wrap items-center gap-3 px-3 py-2">
                  <span className={cn('h-2 w-2 shrink-0 rounded-full', m.dot)} />
                  <span className="font-mono text-[13px] text-ink">{j.scene}</span>
                  <span className="text-[11.5px] text-muted">{fmtDate(j.created_at)}</span>
                  <span className={cn('font-mono text-[11px] uppercase tracking-wide', m.text)}>{m.label}</span>
                  <span className="ml-auto"><DeleteButton onDelete={() => remove(j.id)} /></span>
                </li>
              )
            })}
          </ul>
        </section>
      )}

      <Dialog open={!!playing} onOpenChange={(o) => !o && setPlaying(null)}>
        {playing && (
          <DialogContent className="p-0">
            <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2 pr-12">
              <DialogTitle className="truncate font-mono text-[13px] text-ink">
                {playing.scene} <span className="text-faint">· {playing.id.slice(0, 8)}</span>
              </DialogTitle>
            </div>
            <video className="block max-h-[78vh] w-full bg-black" controls autoPlay src={videoUrl(playing.id)} />
          </DialogContent>
        )}
      </Dialog>
    </main>
  )
}
