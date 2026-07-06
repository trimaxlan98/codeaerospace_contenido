// Panel admin-only de experimentacion: Fable 5 propone primitivas nuevas de
// Manim (Mobjects / Animations) a partir de una descripcion en lenguaje
// natural. Cada propuesta genera un render de muestra por el pipeline normal;
// solo tras aprobacion humana se copia a studio/content/manim_extensions/ (git).

import { useState } from 'react'
import { api, videoUrl } from './api.js'
import { Input } from './components/ui/input.jsx'
import { Button } from './components/ui/button.jsx'

const promptCls = 'w-full resize-y rounded-md border border-line bg-canvas px-3 py-2 text-sm text-ink placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan'

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
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
        <span className="eyebrow">{proposal.slug}</span>
        <span className="font-mono text-[11px] text-faint">{statusLabel(proposal, job)}</span>
      </div>
      <div className="flex flex-col gap-3 p-4">
        <p className="text-[13px] leading-relaxed text-muted">{proposal.description}</p>
        {proposal.explanation && <p className="text-[13px] leading-relaxed text-muted">{proposal.explanation}</p>}
        {proposal.primitive_code && (
          <pre className="max-h-[46vh] w-full overflow-auto whitespace-pre-wrap rounded-md border border-line bg-canvas p-3 font-mono text-[11.5px] leading-relaxed text-[#a8bcd4]">{proposal.primitive_code}</pre>
        )}
        {renderReady && (
          <video key={job.id} className="w-full rounded-md border border-line bg-black" controls preload="metadata"
            src={videoUrl(job.id)} />
        )}
        {(renderReady || proposal.status === 'failed') && (
          <div className="flex flex-wrap gap-2">
            {renderReady && (
              <Button variant="primary" size="sm" disabled={busy}
                onClick={() => wrap(() => onApprove(proposal.id))}>Aprobar</Button>
            )}
            <Button variant="danger" size="sm" disabled={busy}
              onClick={() => wrap(() => onReject(proposal.id))}>Rechazar</Button>
          </div>
        )}
        {canIterate && (
          <div className="flex flex-col gap-2">
            <textarea className={promptCls} rows={2} value={feedback}
              placeholder="feedback para que Fable 5 corrija esta versión…"
              onChange={(e) => setFeedback(e.target.value)} />
            <Button variant="default" size="sm" className="w-fit"
              disabled={busy || feedback.trim().length < 1}
              onClick={() => wrap(async () => { await onIterate(proposal.id, feedback); setFeedback('') })}>
              Iterar con feedback
            </Button>
          </div>
        )}
      </div>
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
      <section className="panel" aria-label="experimentación fable 5">
        <div className="border-b border-line px-3 py-2"><span className="eyebrow">Experimentación · Fable 5</span></div>
        <p className="p-4 text-[13px] text-muted">Fable 5 no está configurado (falta la API key de Anthropic).</p>
      </section>
    )
  }

  const validSlug = /^[a-z0-9][a-z0-9-]*$/.test(slug)

  return (
    <>
      <section className="panel" aria-label="proponer primitiva">
        <div className="border-b border-line px-3 py-2"><span className="eyebrow">Proponer primitiva nueva</span></div>
        <div className="flex flex-col gap-3 p-4">
          <p className="text-[13px] leading-relaxed text-muted">
            Describe un efecto visual nuevo; Fable 5 propone una primitiva de Manim
            (Mobject/Animation) y una escena de muestra, que se renderiza automáticamente
            para tu revisión antes de entrar a la biblioteca.
          </p>
          {error && (
            <p role="alert" className="rounded-md border border-err/40 bg-err/10 px-3 py-2 text-[13px] text-err">{error}</p>
          )}
          <Input value={slug} placeholder="slug (p. ej. disolucion-particulas)"
            onChange={(e) => setSlug(e.target.value)} />
          <textarea className={promptCls} rows={3} value={description}
            placeholder="p. ej. texto que se disuelve en partículas y forma la siguiente ecuación"
            onChange={(e) => setDescription(e.target.value)} />
          <Button variant="default" size="sm" className="w-fit"
            disabled={busy || !validSlug || description.trim().length < 3} onClick={propose}>
            {busy ? 'Enviando…' : 'Proponer a Fable 5'}
          </Button>
        </div>
      </section>

      {primitives.length === 0 ? (
        <p className="px-1 py-2 text-[13px] text-muted">Sin propuestas todavía.</p>
      ) : (
        primitives.map((p) => (
          <ProposalCard key={p.id} proposal={p} job={jobById(p.job_id)}
            onApprove={approve} onReject={reject} onIterate={iterate} />
        ))
      )}
    </>
  )
}
