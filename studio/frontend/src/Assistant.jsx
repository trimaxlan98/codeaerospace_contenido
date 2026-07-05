// Asistente IA (Vertex AI Gemini 2.5). Drawer con 3 acciones: explicar un
// fallo, proponer el script corregido (diff + aplicar) y generar desde texto.
// NUNCA auto-renderiza: todo resultado pasa por el editor y el pipeline normal.

import { useEffect, useRef, useState } from 'react'
import { api } from './api.js'

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
    <pre className="diff" aria-label="diferencias propuestas">
      {rows.map((r, k) => (
        <div key={k} className={r.t === '+' ? 'diff__add' : r.t === '-' ? 'diff__del' : 'diff__ctx'}>
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

  // Auto-ejecucion al abrir via "✨ Explicar error" (un solo disparo por token).
  useEffect(() => {
    if (open && mode === 'explain' && autoRun > ranToken.current) {
      ranToken.current = autoRun
      runExplain()
    }
  }, [open, mode, autoRun]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!open) return null

  return (
    <div className="drawer" role="dialog" aria-label="asistente IA">
      <div className="drawer__box">
        <div className="panel__bar">
          <span className="panel__title">✨ ASISTENTE · GEMINI 2.5</span>
          <button className="btn btn--tiny" onClick={onClose}>Cerrar ✕</button>
        </div>

        <div className="seg drawer__tabs" role="tablist" aria-label="accion">
          {MODES.map((m) => (
            <button key={m.id} role="tab" aria-selected={mode === m.id}
              className={mode === m.id ? 'seg__opt seg__opt--on' : 'seg__opt'}
              onClick={() => { setError(''); onMode(m.id) }}>{m.label}</button>
          ))}
        </div>

        <div className="drawer__body">
          {error && <p className="notice notice--warn" role="alert">{error}</p>}

          {mode === 'explain' && (
            <>
              <p className="drawer__hint">
                {failed
                  ? `Explica en español por qué falló «${job.scene}» (${job.id.slice(0, 8)}).`
                  : 'Selecciona en la cola un render fallido para explicar su error.'}
              </p>
              <button className="btn" disabled={!failed || busy} onClick={runExplain}>
                {busy ? 'Analizando…' : 'Explicar el fallo'}
              </button>
              {explanation && <div className="drawer__answer">{explanation}</div>}
            </>
          )}

          {mode === 'fix' && (
            <>
              <p className="drawer__hint">
                {failed
                  ? `Propone el script corregido de «${job.scene}». Revisa el diff y aplícalo al editor; el render lo lanzas tú.`
                  : 'Selecciona en la cola un render fallido para proponer una corrección.'}
              </p>
              <button className="btn" disabled={!failed || busy} onClick={runFix}>
                {busy ? 'Corrigiendo… (modelo profundo, puede tardar)' : 'Proponer corrección'}
              </button>
              {fixResult && (
                <>
                  <Diff original={fixResult.original} fixed={fixResult.fixed} />
                  <button className="btn btn--primary"
                    onClick={() => { onApply(fixResult.fixed); onClose() }}>
                    Aplicar al editor
                  </button>
                </>
              )}
            </>
          )}

          {mode === 'generate' && (
            <>
              <p className="drawer__hint">
                Describe la animación; el script generado se carga en el editor y
                pasa por la validación y el sandbox de siempre.
              </p>
              <textarea className="drawer__prompt" rows={4} value={prompt}
                maxLength={8000}
                placeholder="p. ej. un péndulo que oscila y dibuja su trayectoria en amarillo"
                onChange={(e) => setPrompt(e.target.value)} />
              <button className="btn" disabled={prompt.trim().length < 3 || busy}
                onClick={runGenerate}>
                {busy ? 'Generando… (modelo profundo, puede tardar)' : 'Generar script'}
              </button>
              {generated && (
                <>
                  <pre className="diff diff--plain">{generated}</pre>
                  <button className="btn btn--primary"
                    onClick={() => { onApply(generated); onClose() }}>
                    Aplicar al editor
                  </button>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
