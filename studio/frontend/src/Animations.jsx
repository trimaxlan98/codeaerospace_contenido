// Biblioteca de animaciones: categorias + lista + vista previa del script,
// con un boton para abrirlo en el Estudio y renderizarlo.

import { useEffect, useMemo, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { api } from './api.js'

export default function Animations({ onOpenInStudio }) {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState('')
  const [catSlug, setCatSlug] = useState(null)
  const [animation, setAnimation] = useState(null) // {id, title, scene, script}
  const [query, setQuery] = useState('')

  useEffect(() => {
    api.animationsIndex()
      .then((d) => {
        setIndex(d)
        if (d.categories.length) setCatSlug(d.categories[0].slug)
      })
      .catch((err) => setError(err.message))
  }, [])

  const cat = index?.categories.find((c) => c.slug === catSlug)
  const list = useMemo(() => {
    if (!cat) return []
    if (!query.trim()) return cat.animations
    const q = query.toLowerCase()
    return cat.animations.filter((a) => a.title.toLowerCase().includes(q))
  }, [cat, query])

  const open = async (id) => {
    setError('')
    try {
      setAnimation(await api.getAnimation(id))
    } catch (err) {
      setError(err.status === 404 ? 'Animación no encontrada' : err.message)
    }
  }

  const totalCount = index
    ? index.categories.reduce((n, c) => n + c.count, 0) : 0

  if (error && !index) return <main className="lessons"><p className="empty">{error}</p></main>
  if (!index) return <main className="lessons"><p className="empty">Cargando animaciones…</p></main>

  return (
    <main className="lessons">
      <aside className="lessons__nav panel">
        <div className="panel__bar"><span className="panel__title">ANIMACIONES</span></div>
        <input className="lessons__search" type="search" placeholder="Buscar…"
          value={query} onChange={(e) => setQuery(e.target.value)}
          aria-label="buscar animaciones" />
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
          {list.map((a) => (
            <li key={a.id}>
              <button
                className={`lessons__item lessons__item--flat${animation?.id === a.id ? ' lessons__item--on' : ''}`}
                onClick={() => open(a.id)}>
                <span className="lessons__ititle">{a.title}</span>
                <span className="lessons__imeta">{a.scene || 'sin escena'}</span>
              </button>
            </li>
          ))}
          {list.length === 0 && <li className="empty">Sin resultados.</li>}
        </ul>
      </aside>

      <section className="lessons__reader panel" aria-label="vista previa">
        {animation ? (
          <>
            <header className="lessons__head" style={{ maxWidth: 'none', margin: '0 0 14px' }}>
              <p className="lessons__crumb">
                {index.categories.find((c) => animation.id.startsWith(c.slug + '/'))?.name}
              </p>
              <h1>{animation.title}</h1>
              <p className="lessons__sub">{animation.scene || 'sin escena detectada'}</p>
            </header>
            <div className="panel__bar">
              <span className="panel__title">{animation.id}.py</span>
              <button className="btn btn--primary"
                onClick={() => onOpenInStudio(animation.script)}>
                Abrir en el Estudio
              </button>
            </div>
            <CodeMirror
              value={animation.script}
              extensions={[python()]}
              theme="dark"
              editable={false}
              className="editor"
              basicSetup={{ foldGutter: false, highlightActiveLine: false }}
            />
          </>
        ) : (
          <div className="lessons__welcome">
            <p className="empty">
              Elige una animación. {totalCount} animaciones
              en {index.categories.length} categorías.
            </p>
          </div>
        )}
        {error && index && <p className="notice notice--warn" role="alert">{error}</p>}
      </section>
    </main>
  )
}
