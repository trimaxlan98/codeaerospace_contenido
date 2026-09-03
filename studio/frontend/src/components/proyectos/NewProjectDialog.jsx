// Alta de proyecto.
//
// Plantillas: el selector arranca SIEMPRE en "En blanco", que reproduce el
// comportamiento de este dialogo antes de que existieran. Quien ya sabe lo
// que hace no paga ni un clic; quien no, se ahorra las ~90 lineas de estilo
// que todos los cursos del repo repiten palabra por palabra.

import { useEffect, useState } from 'react'
import { api } from '../../api.js'
import { PLANTILLAS, plantillaPorId } from '../../plantillas.js'
import { FONDOS, formatoPorId, formatosDe } from '../../formatos.js'
import { Button } from '../ui/button.jsx'
import { Input } from '../ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from '../ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select.jsx'
import { textareaCls } from './meta.js'
import { cn } from '@/lib/utils'

export default function NewProjectDialog({ open, onOpenChange, onCreated }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [quality, setQuality] = useState('qm')
  const [formato, setFormato] = useState('horizontal')
  const [fondo, setFondo] = useState('marca')
  const [styleBlock, setStyleBlock] = useState('')
  const [plantilla, setPlantilla] = useState('blanco')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')

  useEffect(() => {
    if (open) {
      setName(''); setDescription(''); setQuality('qm'); setStyleBlock('')
      setFormato('horizontal'); setFondo('marca'); setPlantilla('blanco')
      setError(''); setBusy('')
    }
  }, [open])

  const elegir = (id) => {
    setPlantilla(id)
    // La calidad y el formato de la plantilla son una sugerencia: los dos
    // campos siguen editables.
    setQuality(plantillaPorId(id).quality)
    setFormato(plantillaPorId(id).formato || 'horizontal')
    setFondo(plantillaPorId(id).fondo || 'marca')
  }

  const tpl = plantillaPorId(plantilla)

  const submit = async (e) => {
    e.preventDefault()
    if (!name.trim() || busy) return
    setBusy('proyecto')
    setError('')
    try {
      const built = tpl.build({ nombre: name.trim() })
      const p = await api.createProject({
        name: name.trim(),
        description,
        quality,
        formato,
        fondo,
        tipo: tpl.tipo || 'curso',
        // El textarea manda si el usuario escribio algo en el.
        style_block: styleBlock || built.styleBlock,
      })
      // Los clips de la plantilla van despues, en orden: si uno falla, el
      // proyecto ya existe y se dice cual quedo a medias en vez de perderlo.
      for (const [i, c] of built.clips.entries()) {
        setBusy(`clips ${i + 1}/${built.clips.length}`)
        await api.createClip(p.id, c)
      }
      onCreated(p)
    } catch (err) {
      setError(err.message)
      setBusy('')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Nuevo proyecto</DialogTitle>
            </div>
            <div className="flex flex-col gap-3 overflow-y-auto p-4">
              <div className="flex flex-col gap-1.5">
                <span className="eyebrow">Empezar desde</span>
                <div role="radiogroup" aria-label="plantilla"
                  className="grid grid-cols-[repeat(auto-fit,minmax(170px,1fr))] gap-2">
                  {PLANTILLAS.map((p) => {
                    const on = p.id === plantilla
                    return (
                      <button key={p.id} type="button" role="radio" aria-checked={on}
                        onClick={() => elegir(p.id)}
                        className={cn(
                          'flex flex-col gap-1 rounded-lg border p-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                          on ? 'border-accent bg-surface-2' : 'border-line hover:border-line-strong',
                        )}>
                        <span className={cn('text-[13px] font-semibold', on ? 'text-accent' : 'text-ink')}>
                          {p.nombre}
                        </span>
                        <span className="text-[11.5px] leading-snug text-muted">{p.resumen}</span>
                        {p.aviso && (
                          <span className="text-[11px] leading-snug text-warn">{p.aviso}</span>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Nombre</span>
                <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus required maxLength={120} />
                <span className="text-[11.5px] text-faint">
                  Para una lección de una familia usa «Familia · 1.1 Título»: la lista
                  agrupa los cursos por ese prefijo.
                </span>
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Descripción</span>
                <Input value={description} onChange={(e) => setDescription(e.target.value)} />
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Calidad</span>
                <Select value={quality} onValueChange={setQuality}>
                  <SelectTrigger className="max-w-[180px]"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ql">480p</SelectItem>
                    <SelectItem value="qm">720p</SelectItem>
                    <SelectItem value="qh">1080p</SelectItem>
                  </SelectContent>
                </Select>
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Formato</span>
                <Select value={formato} onValueChange={setFormato}>
                  <SelectTrigger className="max-w-[220px]"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {formatosDe(tpl.tipo || 'curso').map((f) => (
                      <SelectItem key={f.id} value={f.id}>{f.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span className="text-[11.5px] text-faint">
                  {formatoPorId(formato).hint}. La calidad fija el lado corto:
                  «1080p» son 1920×1080 en horizontal y 1080×1920 en vertical.
                </span>
              </label>
              {(tpl.tipo || 'curso') === 'presentacion' && (
                <label className="flex flex-col gap-1">
                  <span className="eyebrow">Fondo del slide</span>
                  <Select value={fondo} onValueChange={setFondo}>
                    <SelectTrigger className="max-w-[280px]"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {FONDOS.map((f) => (
                        <SelectItem key={f.id} value={f.id}>{f.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <span className="text-[11.5px] text-faint">
                    El texto y los acentos se voltean solos: sobre blanco, el
                    ámbar de la marca daría 2.15:1 de contraste y no se leería.
                  </span>
                </label>
              )}
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Estilo compartido (opcional)</span>
                <textarea value={styleBlock} onChange={(e) => setStyleBlock(e.target.value)} rows={5}
                  placeholder={tpl.id === 'blanco'
                    ? 'Código Python que se antepone a cada clip (imports, colores, helpers…)'
                    : 'Vacío = el estilo de la plantilla. Escribe aquí para reemplazarlo.'}
                  className={cn(textareaCls, 'font-mono')} />
                {tpl.id !== 'blanco' && !styleBlock && (
                  <span className="text-[11.5px] text-faint">
                    {tpl.id === 'promo'
                      ? 'La plantilla pondrá el tema CO.DE Academy sobre el lienzo del formato elegido, con la marca donde la app no la tapa, y creará 1 clip («Promo») que ya renderiza y cierra el bucle.'
                      : tpl.id === 'simulacion'
                        ? 'La plantilla pondrá el tema CO.DE Academy y creará 1 clip («Simulación») que ya renderiza: la simulación (paquete emergencia) es el fondo a pantalla completa y encima van la cifra medida, el HUD y las reglas.'
                        : `La plantilla pondrá el tema oficial CO.DE Academy y creará ${tpl.clips} clips («Clip1…Clip${tpl.clips}») con un arranque que ya renderiza.`}
                    {' '}Todo es editable después.
                  </span>
                )}
              </label>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={Boolean(busy) || !name.trim()}>
                {busy === 'proyecto' ? 'Creando…' : busy ? `Creando ${busy}…` : 'Crear'}
              </Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}
