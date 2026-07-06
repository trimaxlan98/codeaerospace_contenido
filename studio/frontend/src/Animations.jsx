// Biblioteca de animaciones: categorias + lista + vista previa del script,
// con un boton para abrirlo en el Estudio y renderizarlo.

import { useEffect, useMemo, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { api } from './api.js'
import { Input } from './components/ui/input.jsx'
import { Button } from './components/ui/button.jsx'
import { cn } from '@/lib/utils'

export default function Animations({ onOpenInStudio }) {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState('')
  const [catSlug, setCatSlug] = useState(null)
  const [animation, setAnimation] = useState(null) // {id, title, scene, script}
  const [query, setQuery] = useState('')

  useEffect(() => {
    api.animationsIndex()
      .then((d) => {
        // Las categorias sin animaciones (las del curso de Manim) no se
        // muestran en esta pestana.
        const conContenido = { categories: d.categories.filter((c) => c.count > 0) }
        setIndex(conContenido)
        if (conContenido.categories.length) setCatSlug(conContenido.categories[0].slug)
      })
      .catch((err) => setError(err.message))
  }, [])

  const cat = index?.categories.find((c) => c.slug === catSlug)
  const list = useMemo(() => {
    if (!cat) return []
    if (!query.trim()) return cat.animations
    const q = query.toLowerCase()
    return cat.animations.filter((a) => a.title.toLowerCase().includes(q))
  }, [cat, query])

  const open = async (id) => {
    setError('')
    try {
      setAnimation(await api.getAnimation(id))
    } catch (err) {
      setError(err.status === 404 ? 'Animación no encontrada' : err.message)
    }
  }

  const totalCount = index ? index.categories.reduce((n, c) => n + c.count, 0) : 0

  if (error && !index) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">{error}</main>
  }
  if (!index) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">Cargando animaciones…</main>
  }

  const crumb = animation && index.categories.find((c) => animation.id.startsWith(c.slug + '/'))?.name

  return (
    <main className="grid min-h-0 flex-1 gap-3 p-3 lg:grid-cols-[300px_1fr]">
      <aside className="panel flex min-h-0 flex-col overflow-hidden">
        <div className="border-b border-line px-3 py-2"><span className="eyebrow">Animaciones</span></div>
        <div className="p-2.5">
          <Input type="search" placeholder="Buscar…" value={query}
            onChange={(e) => setQuery(e.target.value)} aria-label="buscar animaciones" />
        </div>
        <nav className="flex flex-col gap-0.5 px-2" aria-label="categorías">
          {index.categories.map((c) => {
            const on = c.slug === catSlug
            return (
              <button key={c.slug} onClick={() => { setCatSlug(c.slug); setQuery('') }}
                className={cn(
                  'flex items-center justify-between rounded-md px-2.5 py-1.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                  on ? 'bg-surface-2 text-accent' : 'text-muted hover:bg-surface-2 hover:text-ink',
                )}>
                <span>{c.name}</span>
                <span className="font-mono text-[11px]">{c.count}</span>
              </button>
            )
          })}
        </nav>
        <ul className="mt-1 min-h-0 flex-1 space-y-0.5 overflow-y-auto border-t border-line p-2">
          {list.map((a) => (
            <li key={a.id}>
              <button onClick={() => open(a.id)}
                className={cn(
                  'flex w-full flex-col gap-0.5 rounded-md px-2.5 py-2 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                  animation?.id === a.id ? 'bg-surface-2 outline outline-1 outline-line' : 'hover:bg-surface-2',
                )}>
                <span className="text-[13px] text-ink">{a.title}</span>
                <span className="font-mono text-[11px] text-muted">{a.scene || 'sin escena'}</span>
              </button>
            </li>
          ))}
          {list.length === 0 && <li className="px-2.5 py-3 text-[13px] text-muted">Sin resultados.</li>}
        </ul>
      </aside>

      <section className="panel flex min-h-0 flex-col overflow-hidden" aria-label="vista previa">
        {animation ? (
          <>
            <header className="border-b border-line px-4 py-3">
              <p className="font-mono text-[10.5px] uppercase tracking-[0.16em] text-accent">{crumb}</p>
              <h1 className="mt-1 font-display text-xl font-semibold text-ink">{animation.title}</h1>
              <p className="mt-0.5 text-xs text-muted">{animation.scene || 'sin escena detectada'}</p>
            </header>
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
              <span className="font-mono text-[13px] text-ink">{animation.id}.py</span>
              <Button variant="primary" size="sm" onClick={() => onOpenInStudio(animation.script)}>
                Abrir en el Estudio
              </Button>
            </div>
            <CodeMirror
              value={animation.script}
              extensions={[python()]}
              theme="dark"
              editable={false}
              height="100%"
              className="editor min-h-0 flex-1 overflow-auto text-[13px]"
              basicSetup={{ foldGutter: false, highlightActiveLine: false }}
            />
          </>
        ) : (
          <div className="grid flex-1 place-items-center p-6 text-center">
            <p className="text-[13px] text-muted">
              Elige una animación. {totalCount} animaciones en {index.categories.length} categorías.
            </p>
          </div>
        )}
        {error && index && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>
    </main>
  )
}
