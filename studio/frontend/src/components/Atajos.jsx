// Atajos de teclado de toda la consola, y la hoja que los enseña.
//
// Antes del sprint E4 la app tenía UN atajo (`Ctrl+Enter` para renderizar) y
// no estaba escrito en ninguna parte salvo el `title` de un botón. Aquí viven
// los que hay, en una sola tabla que es a la vez la implementación y la
// documentación: la hoja de ayuda se genera de la misma lista que los liga.
//
// Dos reglas que evitan los errores clásicos de un atajo global:
//
//   - **Nada se dispara mientras se escribe.** Si el foco está en un input,
//     un textarea, un `contenteditable` o el editor de código, las teclas
//     sueltas (`g`, `?`) son texto, no comandos. Sin esto, escribir «gp» en
//     el título de un clip te saca a Proyectos.
//   - **`Ctrl/⌘+K` sí funciona siempre.** Es el que se usa para salir de
//     donde estás, y exigir que sueltes el foco primero lo haría inútil.
//
// El acorde `g` + tecla es el de GitHub/Linear: pulsar `g` arma la segunda
// tecla durante 1,2 s y luego se desarma sola.

import { useEffect, useRef, useState } from 'react'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'

export const ATAJOS = [
  { teclas: ['Ctrl', 'K'], que: 'Paleta de comandos: ir a un curso o a una sección' },
  { teclas: ['g', 'p'], que: 'Ir a Proyectos', view: 'projects' },
  { teclas: ['g', 'e'], que: 'Ir al Estudio', view: 'studio' },
  { teclas: ['g', 'r'], que: 'Ir a Renders', view: 'renders' },
  { teclas: ['g', 'b'], que: 'Ir a la Biblioteca de entregas', view: 'entregas' },
  { teclas: ['g', 'a'], que: 'Ir a Aprender', view: 'learn' },
  { teclas: ['g', 'l'], que: 'Ir al Laboratorio', view: 'lab' },
  { teclas: ['g', 'd'], que: 'Ir a Admin', view: 'admin' },
  { teclas: ['g', 'c'], que: 'Ir a Configuración', view: 'settings' },
  { teclas: ['Ctrl', '↵'], que: 'Renderizar (Estudio) o ejecutar (Laboratorio), desde el editor' },
  { teclas: ['?'], que: 'Esta hoja' },
]

const IR_A = Object.fromEntries(
  ATAJOS.filter((a) => a.view).map((a) => [a.teclas[1], a.view]),
)

const MS_ACORDE = 1200

function escribiendo(el) {
  if (!el) return false
  if (el.isContentEditable) return true
  const tag = el.tagName
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT'
    // CodeMirror 6 monta su superficie editable como un div con este rol.
    || Boolean(el.closest?.('.cm-editor'))
}

/** Liga los atajos globales. Devuelve el estado de los dos diálogos. */
export function useAtajos(navigate) {
  const [paleta, setPaleta] = useState(false)
  const [ayuda, setAyuda] = useState(false)
  const armado = useRef(0)

  useEffect(() => {
    const onKey = (e) => {
      const mod = e.ctrlKey || e.metaKey
      if (mod && e.key.toLowerCase() === 'k') {
        // Este gana incluso dentro del editor: es el atajo para SALIR de
        // donde estas.
        e.preventDefault()
        setPaleta((v) => !v)
        return
      }
      if (mod || e.altKey || escribiendo(e.target)) return

      if (e.key === '?') { e.preventDefault(); setAyuda(true); return }
      if (e.key === 'g') { armado.current = Date.now(); return }
      if (Date.now() - armado.current < MS_ACORDE) {
        const view = IR_A[e.key.toLowerCase()]
        if (view) { e.preventDefault(); armado.current = 0; navigate(view) }
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [navigate])

  return { paleta, setPaleta, ayuda, setAyuda }
}

export function AtajosDialog({ open, onOpenChange }) {
  if (!open) return null
  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent className="p-0 sm:max-w-[440px]">
        <div className="border-b border-line px-4 py-3 pr-12">
          <DialogTitle className="font-display text-[15px] text-ink">
            Atajos de teclado
          </DialogTitle>
        </div>
        <ul className="flex flex-col gap-1.5 p-4">
          {ATAJOS.map((a) => (
            <li key={a.teclas.join('+')} className="flex items-center gap-3 text-[13px]">
              <span className="flex shrink-0 gap-1">
                {a.teclas.map((t) => (
                  <kbd key={t} className="rounded border border-line bg-surface-2 px-1.5 py-0.5 font-mono text-[11px] text-ink">
                    {t}
                  </kbd>
                ))}
              </span>
              <span className="text-muted">{a.que}</span>
            </li>
          ))}
        </ul>
        <p className="border-t border-line px-4 py-2.5 text-[12px] text-faint">
          Las teclas sueltas no hacen nada mientras escribes en un campo o en el
          editor. <kbd className="font-mono">Ctrl+K</kbd> sí funciona siempre.
        </p>
      </DialogContent>
    </Dialog>
  )
}
