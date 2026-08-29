// «Abrir como presentación»: convierte una animación de la Biblioteca en un
// proyecto de tipo presentación, listo para renderizar y salir como .pptx.
//
// Existe porque las ~60 animaciones de `studio/content/animations/` ya son
// material de charla: rehacerlas para una conferencia sería absurdo. Lo que
// costaba era el trámite — crear el proyecto, pegar el script, crear el clip.
//
// Lo que NO hace, y por eso el diálogo lo dice en vez de callarlo:
//
//   · No añade los puntos de clic. Una animación de curso no los tiene, así
//     que sale como UN slide. Se añaden después con `paso()`, y el diálogo
//     deja escrita la línea exacta.
//   · No repinta los colores. `adaptar_escenas()` pone el lienzo, el fondo y
//     la marca; los colores que la animación eligió a mano no se pueden
//     adivinar. Por eso el fondo por defecto es el de MARCA: es aquel para el
//     que se dibujó. Elegir uno claro se avisa.

import { useEffect, useState } from 'react'
import { Presentation } from 'lucide-react'
import { api } from '../api.js'
import { FONDOS, fondoPorId, formatosDe } from '../formatos.js'
import { Button } from './ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import { Input } from './ui/input.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'

export default function AbrirComoPresentacion({ animation, open, onOpenChange, onCreated }) {
  const [nombre, setNombre] = useState('')
  const [formato, setFormato] = useState('horizontal')
  const [fondo, setFondo] = useState('marca')
  const [quality, setQuality] = useState('qh')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) {
      setNombre(animation?.title || '')
      setFormato('horizontal'); setFondo('marca'); setQuality('qh')
      setError(''); setBusy(false)
    }
  }, [open, animation])

  const submit = async (e) => {
    e.preventDefault()
    if (!nombre.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      // El estilo compartido va VACÍO a propósito: el script de la animación
      // ya trae sus propios imports, y el lienzo lo garantiza el backend al
      // renderizar (branding.aplicar con tipo='presentacion' anexa
      // `presentacion.adaptar_escenas`). Anteponer un bloque de estilo
      // obligaría a recortarle la cabecera al script, y eso sí se rompe.
      const p = await api.createProject({
        name: nombre.trim(),
        description: `Desde la animación ${animation.id}`,
        quality,
        formato,
        fondo,
        tipo: 'presentacion',
        style_block: '',
      })
      await api.createClip(p.id, {
        title: animation.title,
        scene: animation.scene || '',
        script: animation.script,
      })
      onCreated?.(p.id)
      onOpenChange(false)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  if (!animation) return null
  const claro = fondoPorId(fondo).claro

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">
                Abrir como presentación
              </DialogTitle>
              <p className="mt-0.5 text-[11.5px] text-faint">
                Crea un proyecto que sale como .pptx, con esta animación dentro.
              </p>
            </div>

            <div className="flex flex-col gap-3 overflow-y-auto p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Nombre</span>
                <Input value={nombre} onChange={(e) => setNombre(e.target.value)}
                  autoFocus aria-label="nombre de la presentación" />
              </label>

              <div className="flex flex-wrap gap-3">
                <label className="flex flex-col gap-1">
                  <span className="eyebrow">Formato</span>
                  <Select value={formato} onValueChange={setFormato}>
                    <SelectTrigger className="w-[220px]"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {formatosDe('presentacion').map((f) => (
                        <SelectItem key={f.id} value={f.id}>{f.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
                <label className="flex flex-col gap-1">
                  <span className="eyebrow">Calidad</span>
                  <Select value={quality} onValueChange={setQuality}>
                    <SelectTrigger className="w-[130px]"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ql">480p</SelectItem>
                      <SelectItem value="qm">720p</SelectItem>
                      <SelectItem value="qh">1080p</SelectItem>
                    </SelectContent>
                  </Select>
                </label>
              </div>

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
                {claro ? (
                  <span className="text-[11.5px] text-warn">
                    Esta animación se dibujó para el fondo oscuro de la marca, y
                    sus colores están escritos en el código: sobre un fondo claro
                    saldrán lavados. El lienzo y el fondo sí se aplican — los
                    colores hay que revisarlos a mano en el clip.
                  </span>
                ) : (
                  <span className="text-[11.5px] text-faint">
                    El fondo para el que se dibujó. Cámbialo solo si vas a
                    revisar también sus colores.
                  </span>
                )}
              </label>

              <div className="rounded-md border border-line bg-canvas p-3">
                <p className="text-[12px] text-muted">
                  Saldrá como <strong className="text-ink">un solo slide</strong>:
                  esta animación no tiene puntos de clic. Para que avance con el
                  ponente, abre el clip y añade esta línea donde quieras cada
                  parada:
                </p>
                <code className="mt-1.5 block font-mono text-[12px] text-accent">
                  presentacion.paso(self, "La idea")
                </code>
              </div>

              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>

            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" size="sm"
                onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" size="sm" disabled={busy || !nombre.trim()}>
                <Presentation className="mr-1 h-3.5 w-3.5" />
                {busy ? 'Creando…' : 'Crear presentación'}
              </Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}
