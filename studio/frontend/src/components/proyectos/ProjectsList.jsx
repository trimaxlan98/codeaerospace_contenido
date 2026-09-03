// El indice de cursos.
//
// NO es una rejilla plana: el catalogo real son ~60 proyectos y la mayoria
// pertenece a una *familia* (Aerodinamica 1.1…4.5, Electromagnetismo 1.1…4.3,
// Metrologia optica 1.1…3.3), que en el nombre se escribe "Familia · N.M
// Titulo". Por eso esto es un indice: familias plegables con su progreso
// agregado, buscador y filtro por estado.

import { useCallback, useEffect, useMemo, useState } from 'react'
import { Plus, Search, Upload } from 'lucide-react'
import { api } from '../../api.js'
import { refreshCatalogo, useCatalogo } from '../../catalogo.js'
import ImportarDialog from '../ImportarDialog.jsx'
import { Button } from '../ui/button.jsx'
import { Input } from '../ui/input.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select.jsx'
import FamilyGroup from './FamilyGroup.jsx'
import NewProjectDialog from './NewProjectDialog.jsx'
import ProjectGrid from './ProjectGrid.jsx'
import { CountsLine, NarrBadge, ProgressBar } from './insignias.jsx'
import { FILTERS, groupProjects, matchesFilter, OPEN_KEY, readOpen, totals } from './meta.js'

export default function ProjectsList({ onOpen }) {
  // El indice se comparte con Renders y con la tira de la cola del Estudio
  // (`catalogo.js`): volver a esta vista ya no vuelve a bajar los ~60 cursos.
  const catalogo = useCatalogo()
  const projects = catalogo.loaded ? catalogo.list : null
  const [deleteError, setDeleteError] = useState('')
  const error = deleteError || catalogo.error
  const [newOpen, setNewOpen] = useState(false)
  const [importOpen, setImportOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('todos')
  const [order, setOrder] = useState('actividad')
  const [openFamilies, setOpenFamilies] = useState(readOpen)
  const load = useCallback(() => refreshCatalogo(), [])

  // Stale-while-revalidate: al volver del detalle de un curso la lista se
  // pinta al instante con lo cacheado y se refresca por detras, porque en el
  // detalle se pudo renderizar, narrar o borrar clips y los contadores del
  // indice habrian quedado viejos.
  useEffect(() => { refreshCatalogo() }, [])

  const toggleFamily = (key) => {
    setOpenFamilies((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key); else next.add(key)
      try { localStorage.setItem(OPEN_KEY, JSON.stringify([...next])) } catch { /* no critico */ }
      return next
    })
  }

  const remove = async (id) => {
    setDeleteError('')
    try {
      await api.deleteProject(id)
      load()
    } catch (err) {
      setDeleteError(err.message)
    }
  }

  const q = query.trim().toLowerCase()
  const visible = useMemo(() => (projects || []).filter((p) => (
    matchesFilter(p, filter)
    && (!q || `${p.name} ${p.description || ''}`.toLowerCase().includes(q))
  )), [projects, filter, q])
  const { families, loose } = useMemo(() => groupProjects(visible, order), [visible, order])
  const all = totals(visible)
  // La dimension "narracion" solo entra en la interfaz si el catalogo la usa.
  const showNarr = useMemo(() => (projects || []).some((p) => (p.narrated_count || 0) > 0), [projects])
  // Buscando o filtrando, plegar esconderia justo lo que se busca.
  const forceOpen = Boolean(q) || filter !== 'todos'

  return (
    <main data-view="projects" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="proyectos">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Proyectos</span>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-faint" />
              <Input type="search" value={query} onChange={(e) => setQuery(e.target.value)}
                placeholder="Buscar curso…" aria-label="buscar proyectos"
                className="h-8 w-[190px] pl-8 text-[13px]" />
            </div>
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="h-8 w-[150px]" aria-label="filtrar por estado"><SelectValue /></SelectTrigger>
              <SelectContent>
                {FILTERS.filter((f) => showNarr || !f.narr)
                  .map((f) => <SelectItem key={f.id} value={f.id}>{f.label}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={order} onValueChange={setOrder}>
              <SelectTrigger className="h-8 w-[130px]" aria-label="ordenar"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="actividad">Actividad</SelectItem>
                <SelectItem value="nombre">Nombre</SelectItem>
              </SelectContent>
            </Select>
            <Button size="sm" variant="default" onClick={() => setImportOpen(true)}
              title="mete un curso-como-archivos: un .zip de fuentes o un directorio de studio/content/">
              <Upload className="h-3.5 w-3.5" /> Importar…
            </Button>
            <Button size="sm" variant="primary" onClick={() => setNewOpen(true)}>
              <Plus className="h-3.5 w-3.5" /> Nuevo proyecto
            </Button>
          </div>
        </div>

        {projects != null && projects.length > 0 && (
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 border-b border-line px-3 py-2 text-[12px] text-muted">
            <span className="font-mono text-[11px] text-faint">
              {visible.length}/{projects.length} proyecto{projects.length === 1 ? '' : 's'}
              {families.length > 0 && ` · ${families.length} familia${families.length === 1 ? '' : 's'}`}
            </span>
            <span className="text-faint" aria-hidden="true">·</span>
            <span><CountsLine t={all} /></span>
            {showNarr && <NarrBadge narrated={all.narrated} clips={all.clips} />}
            <ProgressBar rendered={all.rendered} stale={all.stale} total={all.clips}
              className="ml-auto w-full max-w-[220px]" />
          </div>
        )}

        {projects == null ? (
          <p className="p-4 text-[13px] text-muted">Cargando proyectos…</p>
        ) : projects.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">
            Sin proyectos todavía. Crea uno para agrupar clips en un curso con continuidad.
          </p>
        ) : visible.length === 0 ? (
          <p className="p-4 text-[13px] text-muted">
            Ningún curso coincide con la búsqueda o el filtro.
          </p>
        ) : (
          <div className="flex flex-col">
            {families.map((f) => (
              <FamilyGroup key={f.key} name={f.key} items={f.items} showNarr={showNarr}
                open={forceOpen || openFamilies.has(f.key)}
                onToggle={() => toggleFamily(f.key)}
                onOpen={onOpen} onDelete={remove} />
            ))}
            {loose.length > 0 && (
              families.length === 0 ? (
                <ProjectGrid items={loose} showNarr={showNarr} onOpen={onOpen} onDelete={remove} />
              ) : (
                <FamilyGroup name="Cursos sueltos" items={loose} loose showNarr={showNarr}
                  open={forceOpen || openFamilies.has('__sueltos__')}
                  onToggle={() => toggleFamily('__sueltos__')}
                  onOpen={onOpen} onDelete={remove} />
              )
            )}
          </div>
        )}

        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      <NewProjectDialog open={newOpen} onOpenChange={setNewOpen}
        onCreated={(p) => { setNewOpen(false); load(); onOpen(p.id) }} />
      {/* El importador NO cierra solo ni salta al proyecto: el reporte (que
          clips cambiaron, cuales quedaron por re-renderizar) es la mitad del
          valor de importar, y cerrarse encima lo escondia. */}
      <ImportarDialog open={importOpen} onOpenChange={setImportOpen}
        onImported={() => load()} />
    </main>
  )
}
