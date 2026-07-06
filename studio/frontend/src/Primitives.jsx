// Panel admin-only de experimentacion: Fable 5 propone primitivas nuevas de
// Manim (Mobjects / Animations) a partir de una descripcion en lenguaje
// natural. Cada propuesta genera un render de muestra por el pipeline normal;
// solo tras aprobacion humana se copia a studio/content/manim_extensions/ (git).

import { useState } from 'react'
import { api, videoUrl } from './api.js'

function statusLabel(proposal, job) {
  if (proposal.status === 'generating') return 'generando con Fable 5…'
  if (proposal.status === 'failed') return `fallo: ${proposal.error || 'error desconocido'}`
  if (proposal.status === 'approved') return 'aprobada'
  if (proposal.status === 'rejected') return 'rechazada'
  if (proposal.status === 'rendering') {
    if (!job) return 'render en cola…'
    if (job.status === 'done') return 'render listo — revisar'
    if (['queued', 'running'].includes(job.status)) return `render ${job.status}…`
    return `render ${job.status}`
  }
  return proposal.status
}

function ProposalCard({ proposal, job, onApprove, onReject, onIterate }) {
  const [feedback, setFeedback] = useState('')
  const [busy, setBusy] = useState(false)
  const renderReady = proposal.status === 'rendering' && job?.status === 'done'
  const canIterate = proposal.status !== 'generating'

  const wrap = async (fn) => {
    setBusy(true)
    try { await fn() } finally { setBusy(false) }
  }

  return (
    <div className="panel" aria-label={`propuesta ${proposal.slug}`}>
      <div className="panel__bar">
        <span className="panel__title">{proposal.slug.toUpperCase()}</span>
        <span className="panel__aside">{statusLabel(proposal, job)}</span>
      </div>
      <p className="drawer__hint">{proposal.description}</p>
      {proposal.explanation && <p className="drawer__hint">{proposal.explanation}</p>}
      {proposal.primitive_code && (
        <pre className="diff diff--plain">{proposal.primitive_code}</pre>
      )}
      {renderReady && (
        <video key={job.id} className="video" controls preload="metadata"
          src={videoUrl(job.id)} />
      )}
      {(renderReady || proposal.status === 'failed') && (
        <div className="admin__actions">
          {renderReady && (
            <button className="btn btn--primary" disabled={busy}
              onClick={() => wrap(() => onApprove(proposal.id))}>
              Aprobar
            </button>
          )}
          <button className="btn btn--tiny btn--danger" disabled={busy}
            onClick={() => wrap(() => onReject(proposal.id))}>
            Rechazar
          </button>
        </div>
      )}
      {canIterate && (
        <div className="admin__actions">
          <textarea className="drawer__prompt" rows={2} value={feedback}
            placeholder="feedback para que Fable 5 corrija esta version…"
            onChange={(e) => setFeedback(e.target.value)} />
          <button className="btn btn--tiny" disabled={busy || feedback.trim().length < 1}
            onClick={() => wrap(async () => {
              await onIterate(proposal.id, feedback)
              setFeedback('')
            })}>
            Iterar con feedback
          </button>
        </div>
      )}
    </div>
  )
}

export default function Primitives({ fableEnabled, primitives, jobs, onChanged }) {
  const [slug, setSlug] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const jobById = (id) => jobs.find((j) => j.id === id)

  const propose = async () => {
    setBusy(true); setError('')
    try {
      await api.proposePrimitive({ slug, description })
      setSlug(''); setDescription('')
      onChanged()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  const approve = async (id) => { await api.approvePrimitive(id); onChanged() }
  const reject = async (id) => { await api.rejectPrimitive(id); onChanged() }
  const iterate = async (id, feedback) => { await api.iteratePrimitive(id, feedback); onChanged() }

  if (!fableEnabled) {
    return (
      <section className="panel" aria-label="experimentacion fable 5">
        <div className="panel__bar"><span className="panel__title">EXPERIMENTACIÓN · FABLE 5</span></div>
        <p className="empty">Fable 5 no está configurado (falta la API key de Anthropic).</p>
      </section>
    )
  }

  const validSlug = /^[a-z0-9][a-z0-9-]*$/.test(slug)

  return (
    <>
      <section className="panel" aria-label="proponer primitiva">
        <div className="panel__bar">
          <span className="panel__title">PROPONER PRIMITIVA NUEVA</span>
        </div>
        <p className="drawer__hint">
          Describe un efecto visual nuevo; Fable 5 propone una primitiva de Manim
          (Mobject/Animation) y una escena de muestra, que se renderiza automáticamente
          para tu revisión antes de entrar a la biblioteca.
        </p>
        {error && <p className="notice notice--warn" role="alert">{error}</p>}
        <input className="drawer__prompt" style={{ marginBottom: '0.5rem' }}
          value={slug} placeholder="slug (p. ej. disolucion-particulas)"
          onChange={(e) => setSlug(e.target.value)} />
        <textarea className="drawer__prompt" rows={3} value={description}
          placeholder="p. ej. texto que se disuelve en particulas y forma la siguiente ecuación"
          onChange={(e) => setDescription(e.target.value)} />
        <button className="btn" disabled={busy || !validSlug || description.trim().length < 3}
          onClick={propose}>
          {busy ? 'Enviando…' : 'Proponer a Fable 5'}
        </button>
      </section>

      {primitives.length === 0 ? (
        <p className="empty">Sin propuestas todavía.</p>
      ) : (
        primitives.map((p) => (
          <ProposalCard key={p.id} proposal={p} job={jobById(p.job_id)}
            onApprove={approve} onReject={reject} onIterate={iterate} />
        ))
      )}
    </>
  )
}
