// Selector de proveedor de voz + voz. Lo alimenta `GET /api/projects/{pid}/
// narracion` (campo `proveedores`, el catalogo de app/tts.py): cada
// proveedor trae `disponible` y, si no lo esta, el `motivo` — que se enseña
// en vez de dejar una opcion muerta. Sin GCP (facturacion en mora, 2026-09)
// la voz sale de edge-tts o de Piper; con Vertex ademas se escribe el guion.

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

export const PROVEEDOR_LABEL = {
  vertex: 'Gemini', edge: 'Edge', piper: 'Piper', archivo: 'grabación',
}

// Devuelve {proveedor, voz} validos para el catalogo dado (o los por defecto).
export function vozInicial(narracion) {
  const proveedor = narracion?.proveedor || null
  const p = (narracion?.proveedores || []).find((x) => x.id === proveedor)
  return { proveedor, voz: p?.voz_defecto || null }
}

export default function VozSelector({ proveedores = [], value, onChange, disabled, compact = false }) {
  const sintetizan = proveedores.filter((p) => p.id !== 'archivo')
  const actual = sintetizan.find((p) => p.id === value?.proveedor) || null
  const voces = actual?.voces || []

  const setProveedor = (id) => {
    const p = sintetizan.find((x) => x.id === id)
    onChange({ proveedor: id, voz: p?.voz_defecto || p?.voces?.[0]?.id || null })
  }

  return (
    <div className={cn('flex flex-wrap items-center gap-1.5', compact ? '' : 'gap-2')}>
      <Select value={value?.proveedor || ''} onValueChange={setProveedor} disabled={disabled}>
        <SelectTrigger className={cn('h-8 text-[12.5px]', compact ? 'w-[132px]' : 'w-[168px]')}
          aria-label="proveedor de voz">
          <SelectValue placeholder="proveedor" />
        </SelectTrigger>
        <SelectContent>
          {sintetizan.map((p) => (
            <SelectItem key={p.id} value={p.id} disabled={!p.disponible}
              title={p.disponible ? undefined : p.motivo}>
              {p.nombre}{p.disponible ? '' : ` · ${p.motivo || 'no disponible'}`}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select value={value?.voz || ''} onValueChange={(voz) => onChange({ ...value, voz })}
        disabled={disabled || !actual || voces.length === 0}>
        <SelectTrigger className={cn('h-8 text-[12.5px]', compact ? 'w-[176px]' : 'w-[220px]')}
          aria-label="voz">
          <SelectValue placeholder="voz" />
        </SelectTrigger>
        <SelectContent>
          {voces.map((v) => (
            <SelectItem key={v.id} value={v.id}>{v.nombre}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
