// Una tarjeta del indice: el curso visto desde fuera (progreso, calidad,
// ultima actividad) y la puerta a su detalle.

import { formatoPorId } from '../../formatos.js'
import DeleteButton from '../DeleteButton.jsx'
import { CountsLine, NarrBadge, ProgressBar } from './insignias.jsx'
import { QUALITY_LABEL, fmtDate } from './meta.js'

export default function ProjectCard({ project, showNarr, onOpen, onDelete }) {
  const t = { clips: project.clip_count, rendered: project.rendered_count, stale: project.stale_count }
  return (
    <article className="group flex flex-col gap-2 overflow-hidden rounded-lg border border-line bg-surface-2 p-3 transition-colors hover:border-accent/50">
      <button onClick={onOpen}
        className="flex flex-col gap-1.5 rounded-md text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
        <h3 className="flex items-center gap-1.5 truncate font-display text-[14px] font-semibold text-ink" title={project.name}>
          <span className="truncate">{project.label || project.name}</span>
          {project.tipo === 'promo' && (
            <span className="shrink-0 rounded border border-accent/40 px-1 py-px font-mono text-[10px] uppercase tracking-wide text-accent"
              title={`promo de redes · ${formatoPorId(project.formato).label}`}>
              promo
            </span>
          )}
        </h3>
        {project.description && (
          <p className="line-clamp-2 text-[12px] text-muted">{project.description}</p>
        )}
        <p className="text-[11.5px] text-muted"><CountsLine t={t} /></p>
        <ProgressBar rendered={t.rendered} stale={t.stale} total={t.clips} />
        <p className="flex items-center gap-2 font-mono text-[11px] text-faint">
          <span>{QUALITY_LABEL[project.quality] || project.quality} · {fmtDate(project.updated_at)}</span>
          {showNarr && (
            <NarrBadge narrated={project.narrated_count || 0} clips={t.clips} className="ml-auto" />
          )}
        </p>
      </button>
      {/* Borrar solo al pasar por encima (o con foco de teclado): con ~60
          tarjetas en pantalla, un boton destructivo permanente en cada una es
          ruido y riesgo. */}
      <div className="mt-auto flex justify-end opacity-0 transition-opacity focus-within:opacity-100 group-hover:opacity-100">
        <DeleteButton onDelete={onDelete} />
      </div>
    </article>
  )
}
