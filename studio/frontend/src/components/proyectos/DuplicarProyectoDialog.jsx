// Duplicar el proyecto entero. El nombre es obligatorio y tiene que ser
// nuevo: es la clave con la que el importador empareja proyectos, y dos
// cursos con el mismo nombre romperían `subir_curso.py`.

import { useEffect, useState } from 'react'
import { Copy } from 'lucide-react'
import { api } from '../../api.js'
import { Button } from '../ui/button.jsx'
import { Input } from '../ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from '../ui/dialog.jsx'

export default function DuplicarProyectoDialog({ open, onOpenChange, project, onDuplicado }) {
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) { setName(`${project.name} (copia)`); setError(''); setBusy(false) }
  }, [open, project.name])

  const submit = async (e) => {
    e.preventDefault()
    if (!name.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      onDuplicado(await api.duplicarProyecto(project.id, name.trim()))
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Duplicar proyecto</DialogTitle>
            </div>
            <div className="flex flex-col gap-3 p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Nombre de la copia</span>
                <Input value={name} onChange={(e) => setName(e.target.value)}
                  autoFocus required maxLength={120} />
                <span className="text-[11.5px] text-faint">
                  Se copian el estilo compartido, el formato, la calidad, el
                  fondo y los {project.clips?.length || 0} clips (script, escena,
                  notas y cama de sonido). <strong>Los renders no</strong>: un
                  vídeo es de un solo clip.
                </span>
              </label>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy || !name.trim()}>
                <Copy className="h-3.5 w-3.5" /> {busy ? 'Duplicando…' : 'Duplicar'}
              </Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}
