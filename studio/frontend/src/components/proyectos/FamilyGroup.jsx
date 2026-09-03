// Una familia plegable del indice ("Aerodinamica 1.1…4.5") con su progreso
// agregado en la propia cabecera: se sabe como va la familia entera sin
// desplegarla.

import { ChevronDown, ChevronRight, FolderKanban, Layers } from 'lucide-react'
import ProjectGrid from './ProjectGrid.jsx'
import { CountsLine, NarrBadge, ProgressBar } from './insignias.jsx'
import { contar, totals } from './meta.js'

export default function FamilyGroup({ name, items, loose, showNarr, open, onToggle, onOpen, onDelete }) {
  const t = totals(items)
  return (
    <section aria-label={name} className="border-b border-line last:border-b-0">
      <button onClick={onToggle} aria-expanded={open}
        className="flex w-full items-center gap-2.5 px-3 py-2.5 text-left transition-colors hover:bg-surface-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
        {open
          ? <ChevronDown className="h-4 w-4 shrink-0 text-accent" />
          : <ChevronRight className="h-4 w-4 shrink-0 text-muted" />}
        {loose
          ? <FolderKanban className="h-4 w-4 shrink-0 text-muted" />
          : <Layers className="h-4 w-4 shrink-0 text-accent" />}
        <span className="truncate font-display text-[14.5px] font-semibold text-ink">{name}</span>
        <span className="shrink-0 font-mono text-[11px] text-faint">
          {items.length} {contar(items, loose)}
        </span>
        <span className="ml-auto hidden shrink-0 text-[12px] text-muted sm:block"><CountsLine t={t} /></span>
        {showNarr && <NarrBadge narrated={t.narrated} clips={t.clips} className="hidden sm:inline-flex" />}
        <ProgressBar rendered={t.rendered} stale={t.stale} total={t.clips} className="w-20 shrink-0" />
      </button>
      {open && <ProjectGrid items={items} showNarr={showNarr} onOpen={onOpen} onDelete={onDelete} />}
    </section>
  )
}
