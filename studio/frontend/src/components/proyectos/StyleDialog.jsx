// El estilo compartido del proyecto — el codigo que se antepone a TODOS los
// clips antes de renderizar.
//
// Hasta R5a esto era un `<textarea rows={14}`: el unico sitio de la app donde
// se escribe Python sin resaltado, sin numeros de linea y sin sangrado
// automatico, justo el archivo mas peligroso de los dos (un fallo en el
// estilo rompe los N clips del curso, no uno). Ahora es el mismo CodeMirror
// del Estudio, con el mismo `useEditorTheme()`.
//
// Y dice dos cosas que antes solo se sabian leyendo el backend:
//
//   - el DESFASE de lineas (`style_offset`): manim reporta los fallos contra
//     el script compuesto (estilo + clip), asi que el Estudio le resta este
//     numero para señalar la linea del clip. Al editar el estilo, ese numero
//     cambia; verlo aqui explica por que un error "de la linea 120" apunta a
//     la 30 del clip;
//   - si el bloque trae la IDENTIDAD del canal por su cuenta o si
//     ManimStudio se la va a anexar (`app/branding.py`).

import { useEffect, useMemo, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { ShieldCheck, Stamp } from 'lucide-react'
import { api } from '../../api.js'
import { useEditorTheme } from '../../themes.js'
import { Button } from '../ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from '../ui/dialog.jsx'
import { importaPresentacion, styleOffset, traeMarca } from './meta.js'

/** Lo que ManimStudio va a hacer con la identidad de este proyecto. */
function marca(value, tipo) {
  if (tipo === 'presentacion') {
    return importaPresentacion(value)
      ? { propia: true, texto: 'Este estilo importa «presentacion», así que pide su propio lienzo: ManimStudio no le anexa nada.' }
      : { propia: false, texto: 'Este estilo no importa «presentacion». Si el script del clip tampoco, ManimStudio anexa al final del render el bloque que aplica el lienzo del proyecto (formato y fondo) con la paleta volteada. Sin él, una animación escrita para un curso saldría en 16:9 sobre negro aunque el proyecto pida 4:3 sobre blanco.' }
  }
  return traeMarca(value)
    ? { propia: true, texto: 'Este estilo ya aplica la identidad por su cuenta («code_brand»): ManimStudio no le anexa nada.' }
    : { propia: false, texto: 'Este estilo no menciona «code_brand». Si el script del clip tampoco, ManimStudio anexa al final del render el bloque de identidad CO.DE Academy (marca de agua y escuadras). La marca sale igual; simplemente no la controlas tú.' }
}

export default function StyleDialog({ open, onOpenChange, project, onSaved }) {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const temaEditor = useEditorTheme()   // CodeMirror sigue al tema de la app

  useEffect(() => {
    if (open) { setValue(project.style_block || ''); setError('') }
  }, [open, project.style_block])

  const lineas = useMemo(() => (value ? value.split('\n').length : 0), [value])
  const offset = useMemo(() => styleOffset(value), [value])
  const identidad = useMemo(() => marca(value, project.tipo), [value, project.tipo])

  const submit = async (e) => {
    e.preventDefault()
    if (busy) return
    setBusy(true)
    setError('')
    try {
      const updated = await api.patchProject(project.id, { style_block: value })
      onSaved(updated.style_block, updated.updated_at)
      onOpenChange(false)
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
          <form onSubmit={submit} className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Estilo compartido del proyecto</DialogTitle>
            </div>
            <div className="flex min-h-0 flex-col gap-2 overflow-y-auto p-4">
              <p className="text-[12.5px] text-muted">
                Este código se antepone al script de cada clip antes de renderizar
                (imports, colores, helpers de continuidad…). Cambiarlo marca los
                clips ya renderizados como desactualizados.
              </p>

              <div className="min-h-0 overflow-hidden rounded-md border border-line bg-canvas">
                <div className="editor h-[46vh] min-h-[220px]">
                  <CodeMirror
                    value={value}
                    onChange={setValue}
                    extensions={[python()]}
                    theme={temaEditor}
                    height="100%"
                    className="h-full overflow-auto text-[13px]"
                    basicSetup={{ foldGutter: false, highlightActiveLine: true }}
                    aria-label="estilo compartido del proyecto"
                  />
                </div>
              </div>

              <p className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[11px] text-muted">
                <span>{lineas} línea{lineas === 1 ? '' : 's'}</span>
                <span className="text-faint" aria-hidden="true">·</span>
                <span title="manim numera los fallos sobre el script compuesto (estilo + marcador + clip); el Estudio le resta este desfase para señalar la línea del clip">
                  desfase +{offset} línea{offset === 1 ? '' : 's'}
                </span>
              </p>

              <p className="flex items-start gap-2 rounded-md border border-line bg-surface-2 px-2.5 py-2 text-[12px] leading-snug text-muted"
                role="status">
                {identidad.propia
                  ? <ShieldCheck className="mt-px size-3.5 shrink-0 text-ok" aria-hidden="true" />
                  : <Stamp className="mt-px size-3.5 shrink-0 text-accent" aria-hidden="true" />}
                <span>{identidad.texto}</span>
              </p>

              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy}>Guardar</Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}
