// Render en lote y su progreso agregado (sprint R3a).
//
// El equivalente en la terminal es `render_local.py --todos --calidad qh`.
// En la app existía «Re-renderizar desactualizados», que encolaba y después
// dejaba al operador contando tarjetas verdes de una en una: ni «12 de 30»,
// ni cuánto falta, ni si alguno reventó. Eso es lo que pone esta barra.
//
// La calidad es del PROYECTO (todos sus clips tienen que salir del mismo
// tamaño para que `concat -c copy` pegue), así que pedir otra calidad rehace
// el curso entero: el diálogo lo dice antes de encolar nada.

import { useCallback, useEffect, useState } from 'react'
import { Layers } from 'lucide-react'
import { api } from '../api.js'
import { Button } from './ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

const CALIDADES = [{ id: 'ql', label: '480p' }, { id: 'qm', label: '720p' }, { id: 'qh', label: '1080p' }]

export function fmtEta(s) {
  if (s == null) return '—'
  if (s < 60) return `${Math.round(s)} s`
  const m = Math.round(s / 60)
  if (m < 60) return `${m} min`
  return `${Math.floor(m / 60)} h ${String(m % 60).padStart(2, '0')} min`
}

// ── el diálogo que lanza el lote ─────────────────────────────────────────

export function RenderLoteDialog({ open, onOpenChange, project, staleCount, onLanzado }) {
  const [calidad, setCalidad] = useState(project.quality)
  const [alcance, setAlcance] = useState('stale')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) {
      setCalidad(project.quality)
      setAlcance(staleCount > 0 ? 'stale' : 'todos')
      setError(''); setBusy(false)
    }
  }, [open, project.quality, staleCount])

  const cambiaCalidad = calidad !== project.quality
  const total = project.clips?.length || 0

  const lanzar = async () => {
    if (busy) return
    setBusy(true)
    setError('')
    try {
      const res = await api.renderLote(project.id, {
        clips: null,
        calidad: cambiaCalidad ? calidad : null,
        // Cambiar la calidad rehace TODO: el backend lo fuerza igualmente,
        // aquí solo se evita mandar una intención contradictoria.
        force: cambiaCalidad || alcance === 'todos',
      })
      onLanzado?.(res)
      onOpenChange(false)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <div className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Render en lote</DialogTitle>
              <p className="mt-1 text-[12px] leading-snug text-muted">
                Encola los clips en orden en la cola de siempre (un render a la
                vez). Los que ya tengan un render en curso se saltan.
              </p>
            </div>
            <div className="flex flex-col gap-3 p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Qué se renderiza</span>
                <Select value={alcance} onValueChange={setAlcance} disabled={cambiaCalidad}>
                  <SelectTrigger className="max-w-[320px]" aria-label="alcance del lote"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="stale">Solo los desactualizados ({staleCount})</SelectItem>
                    <SelectItem value="todos">Todos los clips ({total})</SelectItem>
                  </SelectContent>
                </Select>
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Calidad</span>
                <Select value={calidad} onValueChange={setCalidad}>
                  <SelectTrigger className="max-w-[180px]" aria-label="calidad del lote"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {CALIDADES.map((c) => <SelectItem key={c.id} value={c.id}>{c.label}</SelectItem>)}
                  </SelectContent>
                </Select>
                <span className="text-[11.5px] text-faint">
                  La calidad es del proyecto, no del render: todos sus clips
                  tienen que salir del mismo tamaño para poder unirse sin
                  recodificar.
                </span>
              </label>
              {cambiaCalidad && (
                <p className="rounded-lg border border-warn/40 bg-warn/10 px-3 py-2 text-[12px] leading-snug text-warn">
                  Cambiar la calidad a{' '}
                  <strong>{CALIDADES.find((c) => c.id === calidad)?.label}</strong>{' '}
                  rehace <strong>los {total} clips</strong>: los vídeos actuales
                  son del tamaño viejo y no se pueden mezclar con los nuevos.
                </p>
              )}
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="button" variant="primary" onClick={lanzar} disabled={busy}>
                <Layers className="h-3.5 w-3.5" /> {busy ? 'Encolando…' : 'Encolar lote'}
              </Button>
            </div>
          </div>
        </DialogContent>
      )}
    </Dialog>
  )
}

// ── la barra de progreso del lote vigente ────────────────────────────────

/** Sondea `GET /{pid}/lote`. Devuelve el lote vigente (o null) y un
 *  `refrescar()` para pedirlo al instante justo despues de encolar.
 *
 *  `jobs` (la cola global, por SSE) hace de disparador: cuando un render
 *  termina, el lote cambia. Con lote ACTIVO se sondea ademas cada 5 s,
 *  porque la ETA baja sola aunque no llegue ningun evento. */
export function useLote(projectId, jobs) {
  const [lote, setLote] = useState(null)

  const refrescar = useCallback(() => api.getLote(projectId)
    .then((r) => setLote(r.lote))
    .catch(() => setLote(null)), [projectId])

  useEffect(() => { refrescar() }, [refrescar, jobs])

  useEffect(() => {
    if (!lote?.activo) return
    const t = setInterval(refrescar, 5000)
    return () => clearInterval(t)
  }, [lote?.activo, refrescar])

  return { lote, refrescar }
}

export function LoteProgreso({ lote }) {
  if (!lote) return null
  const { total, hechos, fallidos, en_curso: enCurso } = lote
  const pct = (n) => (total > 0 ? (n / total) * 100 : 0)
  return (
    <div className="flex flex-col gap-1.5 rounded-lg border border-line bg-surface-2 px-3 py-2"
      role="status" aria-label="progreso del lote de renders">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px]">
        <span className="eyebrow">Lote</span>
        <span className="font-mono text-[13px] font-semibold tabular-nums text-ink">
          {hechos}/{total}
        </span>
        {enCurso > 0 && <span className="text-cyan">renderizando…</span>}
        {fallidos > 0 && (
          <span className="text-warn">{fallidos} fallido{fallidos === 1 ? '' : 's'}</span>
        )}
        {lote.saltados > 0 && (
          <span className="text-muted">{lote.saltados} saltado{lote.saltados === 1 ? '' : 's'}</span>
        )}
        {lote.activo && (
          <span className="font-mono text-[11px] text-muted">
            faltan {fmtEta(lote.eta_s)}
            {lote.media_s != null && ` · ${fmtEta(lote.media_s)}/clip`}
          </span>
        )}
        {!lote.activo && (
          <span className={cn('font-mono text-[11px]', fallidos > 0 ? 'text-warn' : 'text-ok')}>
            terminado
          </span>
        )}
        {lote.derivado && (
          <span className="font-mono text-[10.5px] text-faint"
            title="el backend se reinició: el lote se reconstruye desde los jobs del proyecto">
            derivado
          </span>
        )}
      </div>
      <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-line" aria-hidden="true">
        <div className="bg-ok" style={{ width: `${pct(hechos)}%` }} />
        <div className="bg-cyan" style={{ width: `${pct(enCurso)}%` }} />
        <div className="bg-warn" style={{ width: `${pct(fallidos)}%` }} />
      </div>
    </div>
  )
}
