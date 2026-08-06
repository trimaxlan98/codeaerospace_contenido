// Asistente IA (Vertex AI Gemini 2.5). Drawer con 3 acciones: explicar un
// fallo, proponer el script corregido (diff + aplicar) y generar desde texto.
// NUNCA auto-renderiza: todo resultado pasa por el editor y el pipeline normal.

import { useEffect, useRef, useState } from 'react'
import * as DialogPrimitive from '@radix-ui/react-dialog'
import { Sparkles, X } from 'lucide-react'
import { api } from './api.js'
import { Button } from './components/ui/button.jsx'
import { cn } from '@/lib/utils'

// Diff de lineas por LCS (scripts pequeños: O(n·m) es suficiente).
function diffLines(aText, bText) {
  const a = aText.split('\n')
  const b = bText.split('\n')
  const n = a.length
  const m = b.length
  const dp = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1))
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1])
    }
  }
  const out = []
  let i = 0
  let j = 0
  while (i < n && j < m) {
    if (a[i] === b[j]) { out.push({ t: ' ', line: a[i] }); i++; j++ }
    else if (dp[i + 1][j] >= dp[i][j + 1]) { out.push({ t: '-', line: a[i] }); i++ }
    else { out.push({ t: '+', line: b[j] }); j++ }
  }
  while (i < n) out.push({ t: '-', line: a[i++] })
  while (j < m) out.push({ t: '+', line: b[j++] })
  return out
}

function Diff({ original, fixed }) {
  const rows = diffLines(original, fixed)
  return (
    <pre className="max-h-[46vh] w-full overflow-auto rounded-md border border-line bg-canvas py-2 font-mono text-[11.5px] leading-relaxed"
      aria-label="diferencias propuestas">
      {rows.map((r, k) => (
        <div key={k}
          className={cn('whitespace-pre-wrap break-words px-2.5',
            r.t === '+' ? 'bg-ok/15 text-ok' : r.t === '-' ? 'bg-err/12 text-err' : 'text-[#a8bcd4]')}>
          {r.t} {r.line}
        </div>
      ))}
    </pre>
  )
}

const MODES = [
  { id: 'explain', label: 'Explicar' },
  { id: 'fix', label: 'Corregir' },
  { id: 'generate', label: 'Generar' },
]

const promptCls = 'w-full resize-y rounded-md border border-line bg-canvas px-3 py-2 text-sm text-ink placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan'

export default function Assistant({ open, mode, onMode, onClose, job, jobLogs,
  onApply, autoRun }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [explanation, setExplanation] = useState('')
  const [fixResult, setFixResult] = useState(null) // {original, fixed}
  const [prompt, setPrompt] = useState('')
  const [generated, setGenerated] = useState('')
  const ranToken = useRef(0)

  const failed = job && ['error', 'timeout'].includes(job.status)

  const jobPayload = async () => {
    const d = await api.getScript(job.id)
    return { script: d.script || '', logs: (jobLogs || []).join('\n') }
  }

  const runExplain = async () => {
    if (!failed || busy) return
    setBusy(true); setError(''); setExplanation('')
    try {
      const d = await api.aiExplain(await jobPayload())
      setExplanation(d.explanation)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  const runFix = async () => {
    if (!failed || busy) return
    setBusy(true); setError(''); setFixResult(null)
    try {
      const payload = await jobPayload()
      const d = await api.aiFix(payload)
      setFixResult({ original: payload.script, fixed: d.script })
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  const runGenerate = async () => {
    if (prompt.trim().length < 3 || busy) return
    setBusy(true); setError(''); setGenerated('')
    try {
      const d = await api.aiGenerate({ prompt })
      setGenerated(d.script)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  // Auto-ejecucion al abrir via "Explicar error" (un solo disparo por token).
  useEffect(() => {
    if (open && mode === 'explain' && autoRun > ranToken.current) {
      ranToken.current = autoRun
      runExplain()
    }
  }, [open, mode, autoRun]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <DialogPrimitive.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-[60] bg-black/50 backdrop-blur-sm data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=closed]:animate-out data-[state=closed]:fade-out-0" />
        <DialogPrimitive.Content
          className="fixed inset-y-0 right-0 z-[61] flex w-[min(560px,100%)] flex-col border-l border-line bg-surface shadow-2xl data-[state=open]:animate-in data-[state=open]:slide-in-from-right data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right">
          <div className="flex items-center justify-between gap-2 border-b border-line px-4 py-3">
            <DialogPrimitive.Title className="flex items-center gap-2 font-display text-sm font-semibold text-ink">
              <Sparkles className="h-4 w-4 text-accent" /> Asistente
              <span className="font-mono text-[10px] uppercase tracking-wide text-faint">Gemini 2.5</span>
            </DialogPrimitive.Title>
            <DialogPrimitive.Close className="grid h-8 w-8 place-items-center rounded-md text-muted transition-colors hover:bg-surface-2 hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
              <X className="h-4 w-4" />
              <span className="sr-only">Cerrar</span>
            </DialogPrimitive.Close>
          </div>

          <div className="flex gap-1 border-b border-line px-4 py-2.5" role="tablist" aria-label="acción">
            {MODES.map((m) => {
              const on = mode === m.id
              return (
                <button key={m.id} role="tab" aria-selected={on}
                  onClick={() => { setError(''); onMode(m.id) }}
                  className={cn(
                    'rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                    on ? 'bg-surface-2 text-accent' : 'text-muted hover:text-ink',
                  )}>
                  {m.label}
                </button>
              )
            })}
          </div>

          <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-4">
            {error && (
              <p role="alert" className="rounded-md border border-err/40 bg-err/10 px-3 py-2 text-[13px] text-err">{error}</p>
            )}

            {mode === 'explain' && (
              <>
                <p className="text-[13px] leading-relaxed text-muted">
                  {failed
                    ? `Explica en español por qué falló «${job.scene}» (${job.id.slice(0, 8)}).`
                    : 'Selecciona en la cola un render fallido para explicar su error.'}
                </p>
                <Button variant="default" disabled={!failed || busy} onClick={runExplain} className="w-fit">
                  {busy ? 'Analizando…' : 'Explicar el fallo'}
                </Button>
                {explanation && (
                  <div className="whitespace-pre-wrap rounded-md border border-line bg-canvas p-3 text-[13px] leading-relaxed text-ink">{explanation}</div>
                )}
              </>
            )}

            {mode === 'fix' && (
              <>
                <p className="text-[13px] leading-relaxed text-muted">
                  {failed
                    ? `Propone el script corregido de «${job.scene}». Revisa el diff y aplícalo al editor; el render lo lanzas tú.`
                    : 'Selecciona en la cola un render fallido para proponer una corrección.'}
                </p>
                <Button variant="default" disabled={!failed || busy} onClick={runFix} className="w-fit">
                  {busy ? 'Corrigiendo… (modelo profundo, puede tardar)' : 'Proponer corrección'}
                </Button>
                {fixResult && (
                  <>
                    <Diff original={fixResult.original} fixed={fixResult.fixed} />
                    <Button variant="primary" className="w-fit"
                      onClick={() => { onApply(fixResult.fixed); onClose() }}>
                      Aplicar al editor
                    </Button>
                  </>
                )}
              </>
            )}

            {mode === 'generate' && (
              <>
                <p className="text-[13px] leading-relaxed text-muted">
                  Describe la animación; el script generado se carga en el editor y
                  pasa por la validación y el sandbox de siempre.
                </p>
                <textarea className={promptCls} rows={4} value={prompt} maxLength={8000}
                  placeholder="p. ej. un péndulo que oscila y dibuja su trayectoria en amarillo"
                  onChange={(e) => setPrompt(e.target.value)} />
                <Button variant="default" disabled={prompt.trim().length < 3 || busy}
                  onClick={runGenerate} className="w-fit">
                  {busy ? 'Generando… (modelo profundo, puede tardar)' : 'Generar script'}
                </Button>
                {generated && (
                  <>
                    <pre className="max-h-[46vh] w-full overflow-auto whitespace-pre-wrap rounded-md border border-line bg-canvas p-3 font-mono text-[11.5px] leading-relaxed text-[#a8bcd4]">{generated}</pre>
                    <Button variant="primary" className="w-fit"
                      onClick={() => { onApply(generated); onClose() }}>
                      Aplicar al editor
                    </Button>
                  </>
                )}
              </>
            )}
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}
