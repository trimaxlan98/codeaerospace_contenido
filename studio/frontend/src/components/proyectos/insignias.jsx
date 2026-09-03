// Los distintivos de Proyectos: barra de progreso, linea de contadores,
// narracion agregada, cifra del panel de estado y duracion del clip.
//
// Van juntos porque son las cinco piezas que se repiten en la lista Y en el
// detalle. Ninguna tiene estado: entran datos, sale un nodo.

import { Mic } from 'lucide-react'
import { DURACION, fmtDur } from './meta.js'
import { cn } from '@/lib/utils'

// Barra de progreso de render: verde lo vigente, ambar lo desactualizado.
export function ProgressBar({ rendered, stale, total, className }) {
  if (!total) return null
  const pctOk = (rendered / total) * 100
  const pctStale = (stale / total) * 100
  return (
    <div className={cn('h-1.5 overflow-hidden rounded-full bg-canvas', className)}
      role="progressbar" aria-valuenow={rendered} aria-valuemin={0} aria-valuemax={total}
      aria-label={`${rendered} de ${total} clips renderizados`}>
      <div className="flex h-full">
        <span className="block h-full bg-ok" style={{ width: `${pctOk}%` }} />
        <span className="block h-full bg-warn" style={{ width: `${pctStale}%` }} />
      </div>
    </div>
  )
}

export function CountsLine({ t }) {
  return (
    <>
      {t.clips} clip{t.clips === 1 ? '' : 's'} · {t.rendered} listo{t.rendered === 1 ? '' : 's'}
      {t.stale > 0 && <span className="text-warn"> · {t.stale} desactualizado{t.stale === 1 ? '' : 's'}</span>}
      {t.clips - t.rendered - t.stale > 0 && (
        <span className="text-muted"> · {t.clips - t.rendered - t.stale} sin render</span>
      )}
    </>
  )
}

// Narracion agregada. Se pinta SOLO si el catalogo tiene alguna narracion
// (`showNarr`): con 60 cursos, un "0/5 narrados" repetido en cada tarjeta de
// una instalacion que no usa voz es ruido puro, justo lo que el encargo 5
// prohibe. Antes este dato no existia en la lista: habia que abrir curso por
// curso para saber que faltaba narrar.
export function NarrBadge({ narrated, clips, className }) {
  if (!clips) return null
  const completo = narrated >= clips
  return (
    <span className={cn('inline-flex shrink-0 items-center gap-1 font-mono text-[11px]',
      // `faint` es el token de adorno (3,67:1 en el tema oscuro): esto es un
      // contador que se lee, asi que el caso «sin narrar» usa `muted`, que si
      // cumple AA como texto normal en los cuatro temas.
      completo ? 'text-ok' : narrated > 0 ? 'text-warn' : 'text-muted', className)}
      title={`${narrated} de ${clips} clips con narracion generada`}>
      <Mic className="h-3 w-3" aria-hidden="true" />
      {narrated}/{clips}
    </span>
  )
}

const STAT_TONE = { ok: 'text-ok', warn: 'text-warn', muted: 'text-ink' }

export function Stat({ label, value, detail, tone }) {
  return (
    <div className="rounded-lg border border-line bg-surface-2 px-3 py-2">
      <div className="eyebrow">{label}</div>
      <div className={cn('mt-0.5 font-mono text-[19px] font-semibold leading-none tabular-nums', STAT_TONE[tone] || 'text-ink')}>
        {value}
      </div>
      <div className="mt-1 text-[11.5px] text-muted">{detail}</div>
    </div>
  )
}

// Duracion del clip con el semaforo del formato (28-45 s).
export function DurationBadge({ s, rango = DURACION.curso }) {
  if (s == null) return null
  const fuera = s < rango.min || s > rango.max
  return (
    <span className={cn('rounded-md border px-1.5 py-0.5 font-mono text-[11px] tabular-nums',
      fuera ? 'border-warn/40 text-warn' : 'border-line text-muted')}
      title={fuera
        ? `fuera del rango del formato (${rango.min}-${rango.max} s)`
        : `dentro del rango del formato (${rango.min}-${rango.max} s)`}>
      {fmtDur(s)}
    </span>
  )
}
