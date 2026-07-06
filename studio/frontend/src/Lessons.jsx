// Biblioteca educativa: categorias + lista + lector con progreso de lectura.

import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api.js'
import { renderMarkdown } from './markdown.js'
import { Input } from './components/ui/input.jsx'
import { Button } from './components/ui/button.jsx'
import { cn } from '@/lib/utils'
import 'katex/dist/katex.min.css'

const READ_KEY = 'ms_lessons_read'

function readSet() {
  try { return new Set(JSON.parse(localStorage.getItem(READ_KEY)) || []) }
  catch { return new Set() }
}

const LEVEL_LABEL = { intro: 'intro', medio: 'medio', avanzado: 'avanzado' }

export default function Lessons({ routeId, onRoute, active = true }) {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState('')
  const [catSlug, setCatSlug] = useState(null)
  const [lesson, setLesson] = useState(null) // {id,...,markdown}
  const [query, setQuery] = useState('')
  const [read, setRead] = useState(readSet)
  const [progress, setProgress] = useState(0)
  const readerRef = useRef(null)
  const scrollRef = useRef(0) // scroll del lector, para restaurarlo al volver
  const requestedRef = useRef(null) // ultima leccion pedida (dedupe ruta/clic)

  useEffect(() => {
    api.lessonsIndex()
      .then((d) => {
        // Las categorias sin lecciones (las de dominio, que solo agrupan
        // animaciones) no se muestran en Aprender.
        const conContenido = { categories: d.categories.filter((c) => c.count > 0) }
        setIndex(conContenido)
        if (conContenido.categories.length) setCatSlug(conContenido.categories[0].slug)
      })
      .catch((err) => setError(err.message))
  }, [])

  const cat = index?.categories.find((c) => c.slug === catSlug)
  const list = useMemo(() => {
    if (!cat) return []
    if (!query.trim()) return cat.lessons
    const q = query.toLowerCase()
    return cat.lessons.filter((l) =>
      l.title.toLowerCase().includes(q)
      || l.tags.some((t) => String(t).toLowerCase().includes(q)))
  }, [cat, query])

  const open = async (id, { fromRoute = false } = {}) => {
    requestedRef.current = id
    setError('')
    try {
      const l = await api.getLesson(id)
      setLesson(l)
      setProgress(0)
      scrollRef.current = 0
      readerRef.current?.scrollTo(0, 0)
      if (fromRoute) {
        // Deep-link: alinear la pestana de categoria con la leccion abierta.
        const c = index?.categories.find((c) => id.startsWith(c.slug + '/'))
        if (c) setCatSlug(c.slug)
      }
      setRead((prev) => {
        const next = new Set(prev).add(id)
        localStorage.setItem(READ_KEY, JSON.stringify([...next]))
        return next
      })
    } catch (err) {
      setError(err.status === 404 ? 'Lección no encontrada' : err.message)
    }
  }

  // Clic del usuario: abre y refleja la leccion en el hash (deep-link, atras).
  const openAndRoute = (id) => {
    open(id)
    onRoute?.(id)
  }

  // #/aprender/<id> (carga inicial o atras/adelante) abre esa leccion.
  useEffect(() => {
    if (!index || !routeId || routeId === requestedRef.current) return
    open(routeId, { fromRoute: true })
  }, [index, routeId]) // eslint-disable-line react-hooks/exhaustive-deps

  // La vista vive oculta (keep-alive) y display:none pierde el scroll del
  // lector: al reactivarla se restaura la ultima posicion conocida.
  useEffect(() => {
    if (active && readerRef.current) readerRef.current.scrollTop = scrollRef.current
  }, [active])

  const onScroll = (e) => {
    const el = e.target
    const max = el.scrollHeight - el.clientHeight
    scrollRef.current = el.scrollTop
    setProgress(max > 0 ? Math.min(100, (el.scrollTop / max) * 100) : 100)
  }

  // Categoria de la leccion ABIERTA (no la de la pestana activa: el usuario
  // puede cambiar de pestana con una leccion de otra categoria abierta).
  const lessonCat = lesson && index
    ? index.categories.find((c) => lesson.id.startsWith(c.slug + '/'))
    : null
  const idx = lesson && lessonCat ? lessonCat.lessons.findIndex((l) => l.id === lesson.id) : -1
  const prev = idx > 0 ? lessonCat.lessons[idx - 1] : null
  const next = idx >= 0 && idx < lessonCat.lessons.length - 1 ? lessonCat.lessons[idx + 1] : null
  const html = useMemo(() => (lesson ? renderMarkdown(lesson.markdown) : ''), [lesson])

  if (error && !index) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">{error}</main>
  }
  if (!index) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">Cargando biblioteca…</main>
  }

  return (
    <main className="grid min-h-0 flex-1 gap-3 p-3 lg:grid-cols-[300px_1fr]">
      <aside className="panel flex min-h-0 flex-col overflow-hidden">
        <div className="border-b border-line px-3 py-2"><span className="eyebrow">Aprender</span></div>
        <div className="p-2.5">
          <Input type="search" placeholder="Buscar…" value={query}
            onChange={(e) => setQuery(e.target.value)} aria-label="buscar lecciones" />
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
          {list.map((l) => {
            const on = lesson?.id === l.id
            const isRead = read.has(l.id)
            return (
              <li key={l.id}>
                <button onClick={() => openAndRoute(l.id)}
                  className={cn(
                    'grid w-full grid-cols-[10px_1fr] gap-x-2.5 rounded-md px-2.5 py-2 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                    on ? 'bg-surface-2 outline outline-1 outline-line' : 'hover:bg-surface-2',
                  )}>
                  <span aria-label={isRead ? 'leída' : 'no leída'}
                    className={cn('mt-[5px] h-[7px] w-[7px] rounded-full border',
                      isRead ? 'border-ok bg-ok' : 'border-muted')} />
                  <span className="text-[13px] text-ink">{l.title}</span>
                  <span className="col-start-2 font-mono text-[11px] text-muted">
                    {LEVEL_LABEL[l.level] || l.level} · {l.minutes} min
                  </span>
                </button>
              </li>
            )
          })}
          {list.length === 0 && <li className="px-2.5 py-3 text-[13px] text-muted">Sin resultados.</li>}
        </ul>
      </aside>

      <section className="panel relative flex min-h-0 flex-col overflow-hidden" aria-label="lector">
        {lesson ? (
          <>
            <div className="absolute inset-x-0 top-0 z-[2] h-0.5 bg-line" aria-hidden="true">
              <div className="h-full bg-accent transition-[width] duration-100" style={{ width: `${progress}%` }} />
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto px-8 py-7" onScroll={onScroll} ref={readerRef}>
              <header className="mx-auto mb-5 max-w-[70ch]">
                <p className="font-mono text-[10.5px] uppercase tracking-[0.16em] text-accent">{lessonCat?.name}</p>
                <h1 className="mt-1.5 font-display text-[26px] font-semibold text-ink">{lesson.title}</h1>
                <p className="mt-1 text-xs text-muted">
                  {LEVEL_LABEL[lesson.level] || lesson.level} · {lesson.minutes} min
                  {lesson.tags.length > 0 && <> · {lesson.tags.join(' · ')}</>}
                </p>
              </header>
              <article className="reader" dangerouslySetInnerHTML={{ __html: html }} />
              <footer className="mx-auto mt-8 flex max-w-[70ch] justify-between gap-2.5">
                {prev ? (
                  <Button variant="default" onClick={() => openAndRoute(prev.id)}>← {prev.title}</Button>
                ) : <span />}
                {next && (
                  <Button variant="primary" onClick={() => openAndRoute(next.id)}>{next.title} →</Button>
                )}
              </footer>
            </div>
          </>
        ) : (
          <div className="grid flex-1 place-items-center p-6 text-center">
            <p className="text-[13px] text-muted">
              Elige una lección. {index.categories.reduce((n, c) => n + c.count, 0)} lecciones
              en {index.categories.length} categorías.
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
