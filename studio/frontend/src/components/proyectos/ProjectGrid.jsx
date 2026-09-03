// La rejilla de tarjetas. Vive suelta porque la usan los dos: el grupo de
// familia (plegado) y la lista cuando no hay ninguna familia que agrupar.

import ProjectCard from './ProjectCard.jsx'

export default function ProjectGrid({ items, showNarr, onOpen, onDelete }) {
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-3 p-3.5 pt-1">
      {items.map((p) => (
        <ProjectCard key={p.id} project={p} showNarr={showNarr}
          onOpen={() => onOpen(p.id)} onDelete={() => onDelete(p.id)} />
      ))}
    </div>
  )
}
