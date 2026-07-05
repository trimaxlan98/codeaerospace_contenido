// Biblioteca educativa: categorias + lista + lector con progreso de lectura.

import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api.js'
import { renderMarkdown } from './markdown.js'
import 'katex/dist/katex.min.css'

const READ_KEY = 'ms_lessons_read'

function readSet() {
  try { return new Set(JSON.parse(localStorage.getItem(READ_KEY)) || []) }
  catch { return new Set() }
}

const LEVEL_LABEL = { intro: 'intro', medio: 'medio', avanzado: 'avanzado' }

export default function Lessons() {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState('')
  const [catSlug, setCatSlug] = useState(null)
  const [lesson, setLesson] = useState(null) // {id,...,markdown}
  const [query, setQuery] = useState('')
  const [read, setRead] = useState(readSet)
  const [progress, setProgress] = useState(0)
  const readerRef = useRef(null)

  useEffect(() => {
    api.lessonsIndex()
      .then((d) => {
        setIndex(d)
        if (d.categories.length) setCatSlug(d.categories[0].slug)
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

  const open = async (id) => {
    setError('')
    try {
      const l = await api.getLesson(id)
      setLesson(l)
      setProgress(0)
      readerRef.current?.scrollTo(0, 0)
      setRead((prev) => {
        const next = new Set(prev).add(id)
        localStorage.setItem(READ_KEY, JSON.stringify([...next]))
        return next
      })
    } catch (err) {
      setError(err.status === 404 ? 'Lección no encontrada' : err.message)
    }
  }

  const onScroll = (e) => {
    const el = e.target
    const max = el.scrollHeight - el.clientHeight
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
  const html = useMemo(
    () => (lesson ? renderMarkdown(lesson.markdown) : ''), [lesson])

  if (error && !index) return <main className="lessons"><p className="empty">{error}</p></main>
  if (!index) return <main className="lessons"><p className="empty">Cargando biblioteca…</p></main>

  return (
    <main className="lessons">
      <aside className="lessons__nav panel">
        <div className="panel__bar"><span className="panel__title">APRENDER</span></div>
        <input className="lessons__search" type="search" placeholder="Buscar…"
          value={query} onChange={(e) => setQuery(e.target.value)}
          aria-label="buscar lecciones" />
        <nav className="lessons__cats" aria-label="categorías">
          {index.categories.map((c) => (
            <button key={c.slug}
              className={`lessons__cat${c.slug === catSlug ? ' lessons__cat--on' : ''}`}
              onClick={() => { setCatSlug(c.slug); setQuery('') }}>
              {c.name} <span className="lessons__count">{c.count}</span>
            </button>
          ))}
        </nav>
        <ul className="lessons__list">
          {list.map((l) => (
            <li key={l.id}>
              <button
                className={`lessons__item${lesson?.id === l.id ? ' lessons__item--on' : ''}`}
                onClick={() => open(l.id)}>
                <span className={`lessons__dotread${read.has(l.id) ? ' lessons__dotread--yes' : ''}`}
                  aria-label={read.has(l.id) ? 'leída' : 'no leída'} />
                <span className="lessons__ititle">{l.title}</span>
                <span className="lessons__imeta">
                  {LEVEL_LABEL[l.level] || l.level} · {l.minutes} min
                </span>
              </button>
            </li>
          ))}
          {list.length === 0 && <li className="empty">Sin resultados.</li>}
        </ul>
      </aside>

      <section className="lessons__reader panel" aria-label="lector">
        {lesson ? (
          <>
            <div className="lessons__progress" aria-hidden="true">
              <div style={{ width: `${progress}%` }} />
            </div>
            <div className="lessons__scroll" onScroll={onScroll} ref={readerRef}>
              <header className="lessons__head">
                <p className="lessons__crumb">{lessonCat?.name}</p>
                <h1>{lesson.title}</h1>
                <p className="lessons__sub">
                  {LEVEL_LABEL[lesson.level] || lesson.level} · {lesson.minutes} min
                  {lesson.tags.length > 0 && <> · {lesson.tags.join(' · ')}</>}
                </p>
              </header>
              <article className="reader" dangerouslySetInnerHTML={{ __html: html }} />
              <footer className="lessons__foot">
                {prev ? (
                  <button className="btn" onClick={() => open(prev.id)}>← {prev.title}</button>
                ) : <span />}
                {next && (
                  <button className="btn btn--primary" onClick={() => open(next.id)}>
                    {next.title} →
                  </button>
                )}
              </footer>
            </div>
          </>
        ) : (
          <div className="lessons__welcome">
            <p className="empty">
              Elige una lección. {index.categories.reduce((n, c) => n + c.count, 0)} lecciones
              en {index.categories.length} categorías.
            </p>
          </div>
        )}
        {error && index && <p className="notice notice--warn" role="alert">{error}</p>}
      </section>
    </main>
  )
}
