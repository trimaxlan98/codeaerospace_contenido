// Biblioteca de entregas: navegar `exports/` como carpetas y ver los videos.
//
// «Renders» enseña los *jobs* —un clip suelto, por su escena— y esa es la
// cocina. Lo que se entrega (la película de un curso, las piezas de un
// vertical, el .pptx de una presentación, los bancos de música y efectos)
// vive en `exports/` y no se veía desde ninguna pantalla: había que entrar
// por ssh. Esta vista es el explorador de ese árbol, en solo lectura.

import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ChevronRight, Download, FileText, Film, Folder, HardDrive, Image as ImageIcon,
  Music, Play, RefreshCw, Search, X,
} from 'lucide-react'
import { api, entregaUrl } from './api.js'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import { cn } from '@/lib/utils'

const ICONO = { video: Film, audio: Music, imagen: ImageIcon, texto: FileText }

function tam(bytes) {
  if (!bytes) return '0 B'
  const u = ['B', 'kB', 'MB', 'GB']
  const i = Math.min(u.length - 1, Math.floor(Math.log(bytes) / Math.log(1024)))
  return `${(bytes / 1024 ** i).toFixed(i ? 1 : 0)} ${u[i]}`
}

function dur(s) {
  if (s == null) return null
  const m = Math.floor(s / 60)
  return m ? `${m} min ${String(Math.round(s % 60)).padStart(2, '0')} s` : `${s.toFixed(1)} s`
}

function fecha(ts) {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleString('es', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  })
}

// Migas: "" → Biblioteca; "verticales/sistemas" → Biblioteca / verticales / sistemas
function migas(ruta) {
  const partes = ruta ? ruta.split('/') : []
  return [{ nombre: 'Biblioteca', ruta: '' },
    ...partes.map((p, i) => ({ nombre: p, ruta: partes.slice(0, i + 1).join('/') }))]
}

export default function Biblioteca({ active }) {
  const [ruta, setRuta] = useState('')
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)
  const [query, setQuery] = useState('')
  const [abierto, setAbierto] = useState(null) // archivo que se está viendo

  const cargar = useCallback((r = ruta) => {
    setCargando(true); setError('')
    api.getEntregas(r)
      .then((d) => { setDatos(d); setRuta(d.ruta) })
      .catch((err) => { setError(err.message); setDatos(null) })
      .finally(() => setCargando(false))
  }, [ruta])

  // Se carga al entrar en la vista (está montada siempre, como las demás).
  useEffect(() => { if (active && !datos && !cargando) cargar('') }, [active]) // eslint-disable-line react-hooks/exhaustive-deps

  const ir = (r) => { setAbierto(null); setQuery(''); setRuta(r); cargar(r) }

  const q = query.trim().toLowerCase()
  const carpetas = useMemo(
    () => (datos?.carpetas || []).filter((c) => !q || c.nombre.toLowerCase().includes(q)),
    [datos, q])
  const archivos = useMemo(
    () => (datos?.archivos || []).filter((a) => !q || a.nombre.toLowerCase().includes(q)),
    [datos, q])

  return (
    <main data-view="entregas" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="biblioteca de entregas">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
          <div className="flex min-w-0 flex-wrap items-center gap-1">
            {migas(ruta).map((m, i, todas) => (
              <span key={m.ruta} className="flex items-center gap-1">
                {i > 0 && <ChevronRight className="h-3 w-3 shrink-0 text-faint" aria-hidden="true" />}
                {i === todas.length - 1 ? (
                  <span className="eyebrow">{datos?.titulo || m.nombre}</span>
                ) : (
                  <button type="button" onClick={() => ir(m.ruta)}
                    className="rounded px-1 text-[12.5px] text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                    {m.nombre}
                  </button>
                )}
              </span>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="pointer-events-none absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-faint" aria-hidden="true" />
              <Input value={query} onChange={(e) => setQuery(e.target.value)}
                placeholder="buscar aquí" aria-label="buscar en esta carpeta"
                className="h-8 w-[172px] pl-7 text-[12.5px]" />
            </div>
            <Button size="sm" variant="ghost" onClick={() => cargar(ruta)} disabled={cargando}
              aria-label="actualizar">
              <RefreshCw className={cn('h-3.5 w-3.5', cargando && 'animate-spin')} />
            </Button>
            <span className="flex items-center gap-1 font-mono text-[11px] text-muted">
              <HardDrive className="h-3.5 w-3.5" aria-hidden="true" />
              {tam(datos?.bytes || 0)}
            </span>
          </div>
        </div>

        {error && (
          <p role="alert" className="border-b border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}

        <div className="p-3">
          {datos?.vacio ? (
            <p className="text-[13px] text-muted">
              Todavía no hay entregas. Aquí aparecerán las películas montadas, los
              cursos verticales, las presentaciones y los bancos de música y efectos.
            </p>
          ) : !datos ? (
            <p className="text-[13px] text-muted">{cargando ? 'Leyendo exports…' : ''}</p>
          ) : (
            <>
              {carpetas.length > 0 && (
                <ul className="mb-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                  {carpetas.map((c) => (
                    <li key={c.ruta}>
                      <button type="button" onClick={() => ir(c.ruta)}
                        className="flex w-full items-center gap-2.5 rounded-lg border border-line bg-canvas/40 px-3 py-2.5 text-left transition-colors hover:border-line-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                        <Folder className="h-4 w-4 shrink-0 text-accent" aria-hidden="true" />
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-[13.5px] text-ink">{c.titulo || c.nombre}</span>
                          <span className="block font-mono text-[11px] text-muted">
                            {c.archivos} archivo{c.archivos === 1 ? '' : 's'} · {tam(c.bytes)}
                          </span>
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              {archivos.length > 0 ? (
                <ul className="divide-y divide-line/60 rounded-lg border border-line">
                  {archivos.map((a) => {
                    const Icono = ICONO[a.tipo] || FileText
                    const reproducible = a.tipo === 'video' || a.tipo === 'audio' || a.tipo === 'imagen'
                    return (
                      <li key={a.ruta} className="flex flex-wrap items-center gap-2 px-3 py-2">
                        <Icono className={cn('h-4 w-4 shrink-0', a.tipo === 'video' ? 'text-cyan' : 'text-muted')} aria-hidden="true" />
                        <span className="min-w-0 flex-1 truncate text-[13.5px] text-ink">{a.nombre}</span>
                        {a.duracion != null && (
                          <span className="font-mono text-[11px] text-cyan">{dur(a.duracion)}</span>
                        )}
                        <span className="font-mono text-[11px] text-muted">{tam(a.bytes)}</span>
                        <span className="hidden font-mono text-[11px] text-faint sm:inline">{fecha(a.modificado)}</span>
                        {reproducible && (
                          <Button size="xs" variant="ghost" onClick={() => setAbierto(a)}
                            aria-label={`ver ${a.nombre}`}>
                            <Play className="h-3.5 w-3.5" /> Ver
                          </Button>
                        )}
                        <Button size="xs" variant="ghost" asChild>
                          <a href={entregaUrl(a.ruta)} download={a.nombre} aria-label={`descargar ${a.nombre}`}>
                            <Download className="h-3.5 w-3.5" />
                          </a>
                        </Button>
                      </li>
                    )
                  })}
                </ul>
              ) : carpetas.length === 0 && (
                <p className="text-[13px] text-muted">
                  {q ? 'Nada coincide con la búsqueda.' : 'Esta carpeta está vacía.'}
                </p>
              )}
            </>
          )}
        </div>
      </section>

      {abierto && (
        <section className="panel" aria-label={`vista de ${abierto.nombre}`}>
          <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
            <span className="min-w-0 truncate text-[13px] text-ink">{abierto.nombre}</span>
            <Button size="xs" variant="ghost" onClick={() => setAbierto(null)} aria-label="cerrar">
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
          <div className="flex justify-center bg-canvas/60 p-3">
            {abierto.tipo === 'video' ? (
              // El backend sirve con Range: se puede saltar dentro de una
              // pelicula de media hora sin descargarla entera.
              <video src={entregaUrl(abierto.ruta)} controls preload="metadata"
                className="max-h-[70vh] w-auto max-w-full rounded-md" />
            ) : abierto.tipo === 'audio' ? (
              <audio src={entregaUrl(abierto.ruta)} controls preload="metadata" className="w-full max-w-xl" />
            ) : (
              <img src={entregaUrl(abierto.ruta)} alt={abierto.nombre}
                className="max-h-[70vh] w-auto max-w-full rounded-md" />
            )}
          </div>
        </section>
      )}
    </main>
  )
}
