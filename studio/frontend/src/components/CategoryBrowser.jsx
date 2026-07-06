// Navegacion lateral compartida por Aprender y Animaciones: acordeon de
// categorias (una expande sus items debajo, estilo submenu) y busqueda global
// sobre todo el indice — antes cada busqueda solo filtraba la categoria activa.

import { useEffect, useMemo, useState } from 'react'
import { ChevronRight } from 'lucide-react'
import { Input } from './ui/input.jsx'
import { cn } from '@/lib/utils'

export default function CategoryBrowser({ title, categories, itemsOf, searchText,
  renderItem, activeId, onOpen }) {
  const [query, setQuery] = useState('')
  // null = el acordeon sigue a la categoria del item abierto; '' = todo plegado.
  const [expanded, setExpanded] = useState(null)

  // Al abrir un item (clic o deep-link) volver a seguir su categoria.
  useEffect(() => { setExpanded(null) }, [activeId])

  const catOf = (id) => id && categories.find((c) => id.startsWith(c.slug + '/'))?.slug
  const open = expanded ?? (catOf(activeId) || categories[0]?.slug)

  const q = query.trim().toLowerCase()
  const results = useMemo(() => {
    if (!q) return null
    return categories
      .map((c) => ({ cat: c, items: itemsOf(c).filter((it) => searchText(it).toLowerCase().includes(q)) }))
      .filter((g) => g.items.length > 0)
  }, [q, categories]) // eslint-disable-line react-hooks/exhaustive-deps

  const itemButton = (it) => (
    <button onClick={() => onOpen(it.id)}
      className={cn(
        'w-full rounded-md px-2.5 py-2 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
        activeId === it.id ? 'bg-surface-2 outline outline-1 outline-line' : 'hover:bg-surface-2',
      )}>
      {renderItem(it)}
    </button>
  )

  return (
    <>
      <div className="border-b border-line px-3 py-2"><span className="eyebrow">{title}</span></div>
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
          <ul className="space-y-0.5">
            {categories.map((c) => {
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
                    </ul>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </>
  )
}
