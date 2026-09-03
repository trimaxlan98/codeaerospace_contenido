// Alta de clip: titulo y, si ya se sabe, la escena. El script se escribe
// despues en el Estudio.

import { useEffect, useState } from 'react'
import { api } from '../../api.js'
import { Button } from '../ui/button.jsx'
import { Input } from '../ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from '../ui/dialog.jsx'

export default function AddClipDialog({ open, onOpenChange, projectId, onCreated }) {
  const [title, setTitle] = useState('')
  const [scene, setScene] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) { setTitle(''); setScene(''); setError('') }
  }, [open])

  const submit = async (e) => {
    e.preventDefault()
    if (!title.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      await api.createClip(projectId, { title: title.trim(), scene: scene.trim() })
      onCreated()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Añadir clip</DialogTitle>
            </div>
            <div className="flex flex-col gap-3 p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Título</span>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} autoFocus required maxLength={200} />
              </label>
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Escena (opcional)</span>
                <Input value={scene} onChange={(e) => setScene(e.target.value)} placeholder="NombreDeEscena"
                  className="font-mono" />
              </label>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy || !title.trim()}>Añadir</Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}
