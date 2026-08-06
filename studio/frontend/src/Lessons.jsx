// Biblioteca educativa: categorias + lista + lector con progreso de lectura.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api.js'
import { renderMarkdown } from './markdown.js'
import CategoryBrowser from './components/CategoryBrowser.jsx'
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
  const [lesson, setLesson] = useState(null) // {id,...,markdown}
  const [read, setRead] = useState(readSet)
  const [progress, setProgress] = useState(0)
  const readerRef = useRef(null)
  const endRef = useRef(null) // pie de la leccion: al verlo se marca leida
  const scrollRef = useRef(0) // scroll del lector, para restaurarlo al volver
  const requestedRef = useRef(null) // ultima leccion pedida (dedupe ruta/clic)

  useEffect(() => {
    api.lessonsIndex()
      .then((d) => {
        // Las categorias sin lecciones (las de dominio, que solo agrupan
        // animaciones) no se muestran en Aprender.
        setIndex({ categories: d.categories.filter((c) => c.count > 0) })
      })
      .catch((err) => setError(err.message))
  }, [])

  const markRead = useCallback((id) => {
    setRead((prev) => {
      if (prev.has(id)) return prev
      const next = new Set(prev).add(id)
      try { localStorage.setItem(READ_KEY, JSON.stringify([...next])) } catch { /* no critico */ }
      return next
    })
  }, [])

  const open = async (id) => {
    requestedRef.current = id
    setError('')
    try {
      const l = await api.getLesson(id)
      setLesson(l)
      setProgress(0)
      scrollRef.current = 0
      readerRef.current?.scrollTo(0, 0)
    } catch (err) {
      setError(err.status === 404 ? 'Lección no encontrada' : err.message)
    }
  }

  // Leida al TERMINARLA, no al abrirla: cuando el pie de la leccion entra en
  // pantalla (sirve igual con scroll interno en escritorio y de pagina en movil).
  useEffect(() => {
    if (!lesson || !endRef.current) return
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) markRead(lesson.id)
    }, { threshold: 0.6 })
    io.observe(endRef.current)
    return () => io.disconnect()
  }, [lesson, markRead])

  // Clic del usuario: abre y refleja la leccion en el hash (deep-link, atras).
  const openAndRoute = (id) => {
    open(id)
    onRoute?.(id)
  }

  // #/aprender/<id> (carga inicial o atras/adelante) abre esa leccion;
  // el acordeon sigue solo a la categoria de la leccion abierta.
  useEffect(() => {
    if (!index || !routeId || routeId === requestedRef.current) return
    open(routeId)
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
    <main className="grid min-h-0 flex-1 grid-rows-[auto_1fr] gap-3 p-3 lg:grid-cols-[300px_1fr] lg:grid-rows-1">
      {/* En movil la columna de categorias se acota a media pantalla (la lista
          scrollea por dentro) para que el lector quede al alcance. */}
      <aside className="panel flex max-h-[45dvh] min-h-0 flex-col overflow-hidden lg:max-h-none">
        <CategoryBrowser
          title="Aprender"
          categories={index.categories}
          itemsOf={(c) => c.lessons}
          searchText={(l) => `${l.title} ${l.tags.join(' ')}`}
          activeId={lesson?.id}
          onOpen={openAndRoute}
          renderItem={(l) => (
            <span className="grid grid-cols-[10px_1fr] gap-x-2.5">
              <span aria-label={read.has(l.id) ? 'leída' : 'no leída'}
                className={cn('mt-[5px] h-[7px] w-[7px] rounded-full border',
                  read.has(l.id) ? 'border-ok bg-ok' : 'border-muted')} />
              <span className="text-[13px] text-ink">{l.title}</span>
              <span className="col-start-2 font-mono text-[11px] text-muted">
                {LEVEL_LABEL[l.level] || l.level} · {l.minutes} min
              </span>
            </span>
          )}
        />
      </aside>

      <section className="panel relative flex min-h-[50dvh] flex-col overflow-hidden lg:min-h-0" aria-label="lector">
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
              <footer ref={endRef} className="mx-auto mt-8 flex max-w-[70ch] justify-between gap-2.5">
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
