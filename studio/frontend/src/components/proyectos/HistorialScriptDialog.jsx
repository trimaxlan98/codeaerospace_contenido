// Historial ligero del script de un clip (R5a).
//
// El estudio no guarda versiones, pero SÍ guarda una: la del último render
// que salió bien. `jobs.script` es el script compuesto (estilo + marcador +
// clip) que se mandó al contenedor, y el clip apunta a ese job mientras el
// vídeo siga siendo el vigente. Es decir: cuando un clip está
// `desactualizado`, la app tiene delante las dos versiones —la de ahora y la
// que funcionó— y hasta hoy no las enseñaba.
//
// Dos decisiones:
//
//   - Solo con el clip DESACTUALIZADO. Si está al día, el script del clip y
//     el del render son el mismo por definición (el hash de contenido los
//     compara), así que el botón no diría nada; y si no tiene render, no hay
//     historial que restaurar.
//   - Restaurar es DESTRUCTIVO (se pierde lo que hay escrito ahora), así que
//     confirma en dos toques, como el resto de la app.
//
// Trampa: lo que guarda el job NO es el script del clip, es el compuesto. Sin
// cortar por el marcador del estilo, restaurar habría metido el style_block
// entero DENTRO del script del clip, y el siguiente render lo habría
// antepuesto otra vez: el estilo duplicado, dos veces cada import.

import { useEffect, useMemo, useState } from 'react'
import { History, RotateCcw } from 'lucide-react'
import { api } from '../../api.js'
import { Button } from '../ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from '../ui/dialog.jsx'
import { cuentaCambios, diffLines } from '../../lib/diff.js'
import { QUALITY_LABEL, fmtDate, scriptDelClip } from './meta.js'
import { cn } from '@/lib/utils'

export default function HistorialScriptDialog({ projectId, clip, job, onOpenChange, onRestaurado }) {
  const [actual, setActual] = useState(null)
  const [delRender, setDelRender] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [armado, setArmado] = useState(false)
  const open = Boolean(clip)

  useEffect(() => {
    if (!clip) return
    let vivo = true
    setActual(null); setDelRender(null); setError(''); setArmado(false)
    Promise.all([
      api.getClipScript(projectId, clip.id),
      api.getScript(clip.job_id),
    ]).then(([mio, delJob]) => {
      if (!vivo) return
      setActual(mio.script || '')
      setDelRender(scriptDelClip(delJob.script || ''))
    }).catch((err) => { if (vivo) setError(err.message) })
    return () => { vivo = false }
  }, [projectId, clip])

  // El botón se desarma solo, igual que `DeleteButton`.
  useEffect(() => {
    if (!armado) return
    const t = setTimeout(() => setArmado(false), 3500)
    return () => clearTimeout(t)
  }, [armado])

  const filas = useMemo(
    () => (actual == null || delRender == null ? null : diffLines(actual, delRender)),
    [actual, delRender])
  const cambios = filas ? cuentaCambios(filas) : null
  const iguales = cambios != null && cambios.quitadas === 0 && cambios.anadidas === 0

  const restaurar = async () => {
    setBusy(true); setError('')
    try {
      await api.patchClip(projectId, clip.id, { script: delRender })
      onRestaurado()
    } catch (err) {
      setError(err.message)
      setBusy(false)
      setArmado(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onOpenChange(false)}>
      {open && (
        <DialogContent className="p-0">
          <div className="flex max-h-[85vh] flex-col">
            <div className="flex flex-col gap-1 border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="flex items-center gap-2 font-display text-[15px] text-ink">
                <History className="size-4 text-accent" aria-hidden="true" />
                El script del último render de «{clip.title}»
              </DialogTitle>
              {job && (
                <p className="font-mono text-[11px] text-faint">
                  {job.scene} · {QUALITY_LABEL[job.quality] || job.quality} · {fmtDate(job.finished_at || job.created_at)}
                </p>
              )}
            </div>

            <div className="flex min-h-0 flex-col gap-2 overflow-y-auto p-4">
              <p className="text-[12.5px] text-muted">
                Este clip está desactualizado: lo que hay escrito ahora no es lo
                que produjo el vídeo vigente. Abajo, lo que cambiaría al
                restaurar — <span className="text-err">en rojo</span> lo que se
                quita, <span className="text-ok">en verde</span> lo que vuelve.
                El estilo compartido no entra: se antepone en cada render.
              </p>

              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}

              {filas == null && !error && (
                <p className="text-[13px] text-muted">Leyendo las dos versiones…</p>
              )}

              {cambios && (
                <p role="status" className="font-mono text-[11.5px] text-muted">
                  {iguales
                    ? 'Las dos versiones son idénticas: lo que cambió fue el estilo compartido o la escena.'
                    : `${cambios.quitadas + cambios.anadidas} línea${cambios.quitadas + cambios.anadidas === 1 ? '' : 's'} distinta${cambios.quitadas + cambios.anadidas === 1 ? '' : 's'} · −${cambios.quitadas} / +${cambios.anadidas}`}
                </p>
              )}

              {filas && !iguales && (
                <pre className="max-h-[46vh] w-full overflow-auto rounded-md border border-line bg-canvas py-2 font-mono text-[11.5px] leading-relaxed"
                  aria-label="diferencias con el script del último render">
                  {filas.map((r, k) => (
                    <div key={k}
                      className={cn('whitespace-pre-wrap break-words px-2.5',
                        r.t === '+' ? 'bg-ok/15 text-ok' : r.t === '-' ? 'bg-err/12 text-err' : 'text-code-ink')}>
                      {r.t} {r.line}
                    </div>
                  ))}
                </pre>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cerrar</Button>
              {armado ? (
                <Button type="button" variant="danger" onClick={restaurar} disabled={busy}>
                  {busy ? 'Restaurando…' : 'Se perderá lo escrito. ¿Confirmar?'}
                </Button>
              ) : (
                <Button type="button" variant="primary" onClick={() => setArmado(true)}
                  disabled={filas == null || iguales || busy}
                  title={iguales ? 'no hay nada que restaurar: el script es el mismo' : undefined}>
                  <RotateCcw className="h-3.5 w-3.5" /> Restaurar este script
                </Button>
              )}
            </div>
          </div>
        </DialogContent>
      )}
    </Dialog>
  )
}
