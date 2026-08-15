// Navegacion lateral de Aprender: grupos > categorias (acordeon) > items, con
// busqueda global sobre TODO el indice.
//
// Antes esta barra la compartian dos vistas hermanas (Aprender y Animaciones)
// que leian el mismo `categories.yaml` del backend y se ignoraban entre si:
// buscar "orbita" en Aprender no encontraba la animacion de orbita. Al
// fusionarlas (sprint 4) la barra pasa a tener GRUPOS — "Curso de Manim" con
// las lecciones y "Animaciones" con los ejemplos por dominio — y una sola
// busqueda que los recorre todos.

import { useEffect, useMemo, useState } from 'react'
import { ChevronRight, Plus } from 'lucide-react'
import { Input } from './ui/input.jsx'
import { cn } from '@/lib/utils'

/**
 * @param groups      [{ id, label, categories, onAddCategory?, addItemLabel? }]
 * @param itemsOf     (categoria) => items
 * @param searchText  (item) => texto sobre el que buscar
 * @param renderItem  (item) => JSX de la fila
 * @param activeId    id del item abierto (para seguir su categoria)
 * @param onOpen      (id) => void
 * @param onAddItem   (categoria) => void  (solo en grupos con addItemLabel)
 */
export default function CategoryBrowser({ title, groups, itemsOf, searchText,
  renderItem, activeId, onOpen, onAddItem }) {
  const [query, setQuery] = useState('')
  // null = el acordeon sigue a la categoria del item abierto; '' = todo plegado.
  const [expanded, setExpanded] = useState(null)

  // Al abrir un item (clic o deep-link) volver a seguir su categoria.
  useEffect(() => { setExpanded(null) }, [activeId])

  const allCats = useMemo(() => groups.flatMap((g) => g.categories), [groups])
  const catOf = (id) => id && allCats.find((c) => id.startsWith(c.slug + '/'))?.slug
  const open = expanded ?? (catOf(activeId) || allCats[0]?.slug)

  const q = query.trim().toLowerCase()
  const results = useMemo(() => {
    if (!q) return null
    return allCats
      .map((c) => ({ cat: c, items: itemsOf(c).filter((it) => searchText(it).toLowerCase().includes(q)) }))
      .filter((g) => g.items.length > 0)
  }, [q, allCats]) // eslint-disable-line react-hooks/exhaustive-deps

  const itemButton = (it) => (
    <button onClick={() => onOpen(it.id)}
      className={cn(
        'w-full rounded-md px-2.5 py-2 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
        activeId === it.id ? 'bg-surface-2 outline outline-1 outline-line' : 'hover:bg-surface-2',
      )}>
      {renderItem(it)}
    </button>
  )

  const categoryItem = (c, group) => {
    const on = c.slug === open
    return (
      <li key={c.slug}>
        <button aria-expanded={on}
          onClick={() => setExpanded(on ? '' : c.slug)}
          className={cn(
            'flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
            on ? 'text-accent' : 'text-muted hover:bg-surface-2 hover:text-ink',
          )}>
          <ChevronRight className={cn('h-3.5 w-3.5 shrink-0 transition-transform', on && 'rotate-90')} />
          <span className="flex-1 text-left">{c.name}</span>
          <span className="font-mono text-[11px]">{c.count}</span>
        </button>
        {on && (
          <ul className="mb-1 ml-[15px] space-y-0.5 border-l border-line pl-1.5 pt-0.5">
            {itemsOf(c).map((it) => <li key={it.id}>{itemButton(it)}</li>)}
            {group.addItemLabel && onAddItem && (
              <li>
                <button onClick={() => onAddItem(c)}
                  className="flex w-full items-center gap-1.5 rounded-md px-2.5 py-1.5 text-left text-[12.5px] text-muted transition-colors hover:bg-surface-2 hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                  <Plus className="h-3.5 w-3.5 shrink-0" /> {group.addItemLabel}
                </button>
              </li>
            )}
          </ul>
        )}
      </li>
    )
  }

  return (
    <>
      <div className="flex items-center justify-between border-b border-line px-3 py-2">
        <span className="eyebrow">{title}</span>
      </div>
      <div className="p-2.5 pb-2">
        <Input type="search" placeholder="Buscar en todo…" value={query}
          onChange={(e) => setQuery(e.target.value)} aria-label={`buscar en ${title}`} />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-2">
        {results ? (
          results.length === 0 ? (
            <p className="px-2.5 py-3 text-[13px] text-muted">Sin resultados en todo el índice.</p>
          ) : (
            results.map(({ cat, items }) => (
              <section key={cat.slug} aria-label={cat.name}>
                <p className="eyebrow px-2.5 pb-1 pt-2.5">{cat.name}</p>
                <ul className="space-y-0.5">
                  {items.map((it) => <li key={it.id}>{itemButton(it)}</li>)}
                </ul>
              </section>
            ))
          )
        ) : (
          groups.map((g) => (
            g.categories.length === 0 ? null : (
              <section key={g.id} aria-label={g.label} className="pb-1">
                <div className="flex items-center gap-2 px-2 pb-1 pt-2.5">
                  <span className="eyebrow">{g.label}</span>
                  {/* Progreso del grupo (p. ej. 8/18 lecciones leidas). */}
                  {g.badge && (
                    <span className="font-mono text-[11px] text-muted" title="lecciones leídas">
                      {g.badge}
                    </span>
                  )}
                  {g.onAddCategory && (
                    <button onClick={g.onAddCategory} title="Nueva sección"
                      className="ml-auto flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11.5px] text-muted transition-colors hover:bg-surface-2 hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                      <Plus className="h-3.5 w-3.5" /> Sección
                    </button>
                  )}
                </div>
                <ul className="space-y-0.5">
                  {g.categories.map((c) => categoryItem(c, g))}
                </ul>
              </section>
            )
          ))
        )}
      </div>
    </>
  )
}
