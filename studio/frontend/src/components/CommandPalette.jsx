// Paleta de comandos (Ctrl+K / ⌘K): ir a cualquier sitio escribiendo.
//
// El catálogo real son ~80 cursos y ~400 clips. Llegar a «Álgebra lineal · 4.2
// Diagonalizar» costaba: Proyectos → desplegar la familia → buscar la lección
// → abrirla. Cuatro gestos para algo que se sabe de memoria.
//
// Decisiones:
//
//   - **Las fuentes son las que ya hay**: el store compartido del catálogo
//     (`catalogo.js`) y la tabla de vistas del router. La paleta no pide nada
//     al servidor; se abre instantánea porque el índice ya está en memoria.
//   - **Se puntúa, no se filtra**: escribir «alg 42» tiene que encontrar
//     «Álgebra lineal · 4.2 Diagonalizar». Un `includes()` de la cadena
//     completa no lo hace; una coincidencia por trozos (todas las palabras,
//     en cualquier orden) sí.
//   - **Sin acentos**: nadie escribe «Álgebra» con tilde en un buscador.
//   - **La lista vacía enseña las vistas**, no un hueco: abrir la paleta sin
//     saber qué buscar tiene que enseñar qué se puede hacer.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Activity, FileCode, Film, FolderKanban, GraduationCap, Search, Settings,
} from 'lucide-react'
import { splitName, useCatalogo } from '../catalogo.js'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import { cn } from '@/lib/utils'

const VISTAS = [
  { view: 'projects', label: 'Proyectos', icon: FolderKanban },
  { view: 'studio', label: 'Estudio', icon: FileCode },
  { view: 'renders', label: 'Renders', icon: Film },
  { view: 'learn', label: 'Aprender', icon: GraduationCap },
  { view: 'admin', label: 'Admin', icon: Activity },
  { view: 'settings', label: 'Configuración', icon: Settings },
]

/** Sin tildes y en minúsculas: nadie teclea «Álgebra» con tilde. */
export function plano(s) {
  return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

/** Solo letras y dígitos: «4.2» y «42» tienen que ser lo mismo.
 *  Nadie teclea el punto de «Álgebra lineal · 4.2» al buscar. */
function compacto(s) {
  return plano(s).replace(/[^a-z0-9]/g, '')
}

/** Puntuación de `texto` contra la consulta, o -1 si no encaja.
 *  Todas las palabras de la consulta tienen que aparecer; cuanto antes
 *  empiecen y menos texto sobre, mejor. Una palabra que no aparece tal cual
 *  se reintenta contra el texto compactado (así «alg 42» encuentra
 *  «Álgebra lineal · 4.2 Diagonalizar»), y esa coincidencia puntúa algo peor
 *  que la literal para que la exacta gane cuando existen las dos. */
export function puntuar(texto, consulta) {
  const t = plano(texto)
  const tc = compacto(texto)
  const palabras = plano(consulta).split(/\s+/).filter(Boolean)
  if (!palabras.length) return 0
  let total = 0
  for (const p of palabras) {
    const i = t.indexOf(p)
    if (i >= 0) {
      // Empezar por el principio de una palabra vale más que caer en medio.
      total += (i === 0 || t[i - 1] === ' ' ? 0 : 40) + i
      continue
    }
    const j = tc.indexOf(compacto(p))
    if (j < 0) return -1
    total += 60 + j
  }
  return total + t.length / 100
}

export default function CommandPalette({ open, onOpenChange, onNavigate }) {
  const catalogo = useCatalogo()
  const [q, setQ] = useState('')
  const [sel, setSel] = useState(0)
  const listaRef = useRef(null)

  useEffect(() => { if (open) { setQ(''); setSel(0) } }, [open])

  const items = useMemo(() => {
    const base = VISTAS.map((v) => ({
      id: `vista:${v.view}`, tipo: 'Ir a', label: v.label, icon: v.icon,
      accion: () => onNavigate(v.view),
    }))
    const cursos = (catalogo.list || []).map((p) => {
      const { family, label } = splitName(p.name)
      return {
        id: `curso:${p.id}`,
        tipo: family || 'Curso',
        familia: family,
        label,
        detalle: `${p.rendered_count ?? 0}/${p.clip_count ?? 0} clips`,
        buscar: p.name,
        icon: FolderKanban,
        accion: () => onNavigate('projects', p.id),
      }
    })
    return [...base, ...cursos]
  }, [catalogo, onNavigate])

  const resultados = useMemo(() => {
    if (!q.trim()) return items.slice(0, VISTAS.length)
    return items
      .map((it) => ({ it, p: puntuar(`${it.tipo} ${it.buscar || it.label}`, q) }))
      .filter(({ p }) => p >= 0)
      .sort((a, b) => a.p - b.p)
      .slice(0, 40)
      .map(({ it }) => it)
  }, [items, q])

  useEffect(() => { setSel(0) }, [q])

  // La selección tiene que verse aunque se navegue con el teclado por una
  // lista de 40: sin esto, la fila activa se queda fuera del scroll.
  useEffect(() => {
    listaRef.current?.querySelector('[data-sel="true"]')
      ?.scrollIntoView({ block: 'nearest' })
  }, [sel, resultados.length])

  const elegir = useCallback((it) => {
    if (!it) return
    onOpenChange(false)
    it.accion()
  }, [onOpenChange, onNavigate]) // eslint-disable-line react-hooks/exhaustive-deps

  const onKeyDown = (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setSel((s) => Math.min(s + 1, resultados.length - 1)) }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setSel((s) => Math.max(s - 1, 0)) }
    else if (e.key === 'Enter') { e.preventDefault(); elegir(resultados[sel]) }
  }

  if (!open) return null

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent className="p-0 sm:max-w-[560px]">
        <DialogTitle className="sr-only">Paleta de comandos</DialogTitle>
        <div className="flex items-center gap-2 border-b border-line px-3 py-2.5">
          <Search className="h-4 w-4 shrink-0 text-muted" />
          <input
            autoFocus value={q} onChange={(e) => setQ(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ir a un curso o a una sección…"
            aria-label="Buscar en la consola"
            className="w-full bg-transparent pr-8 text-[14px] text-ink placeholder:text-faint focus-visible:outline-none" />
        </div>

        <div ref={listaRef} className="max-h-[52vh] overflow-y-auto py-1">
          {resultados.length === 0 ? (
            <p className="px-3 py-4 text-[13px] text-muted">Nada con «{q}».</p>
          ) : resultados.map((it, i) => {
            const Icon = it.icon
            return (
              <button key={it.id} data-sel={i === sel} onClick={() => elegir(it)}
                onMouseMove={() => setSel(i)}
                className={cn(
                  'flex w-full items-center gap-2.5 px-3 py-2 text-left text-[13px]',
                  i === sel ? 'bg-surface-2 text-ink' : 'text-muted')}>
                <Icon className={cn('h-3.5 w-3.5 shrink-0',
                  i === sel ? 'text-accent' : 'text-faint')} />
                {/* La familia va DELANTE, no en la columna derecha: «1.1 El
                    vector» existe en Algebra lineal y en Calculo vectorial, y
                    sin la familia las dos filas son la misma. */}
                <span className="truncate">
                  {it.familia && (
                    <span className={i === sel ? 'text-muted' : 'text-faint'}>{it.familia} · </span>
                  )}
                  {it.label}
                </span>
                {/* La fila seleccionada sube TODA de tono, no solo su rotulo y
                    su icono: sobre `bg-surface-2` dentro del dialogo (dos
                    velos apilados) `faint` se queda en 4,07:1, y esta columna
                    dice de que tipo es el resultado — es dato, no adorno. */}
                <span className={cn('ml-auto shrink-0 truncate pl-3 font-mono text-[11px]',
                  i === sel ? 'text-muted' : 'text-faint')}>
                  {it.detalle || it.tipo}
                </span>
              </button>
            )
          })}
        </div>

        <div className="flex items-center gap-3 border-t border-line px-3 py-2 font-mono text-[10.5px] text-faint">
          <span>↑↓ moverse</span><span>↵ abrir</span><span className="ml-auto">? atajos</span>
        </div>
      </DialogContent>
    </Dialog>
  )
}
