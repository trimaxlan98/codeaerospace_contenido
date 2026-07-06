// Biblioteca de animaciones: categorias + lista + vista previa del script,
// con un boton para abrirlo en el Estudio y renderizarlo.

import { useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { api } from './api.js'
import CategoryBrowser from './components/CategoryBrowser.jsx'
import { Button } from './components/ui/button.jsx'

export default function Animations({ onOpenInStudio, routeId, onRoute }) {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState('')
  const [animation, setAnimation] = useState(null) // {id, title, scene, script}
  const requestedRef = useRef(null) // ultima animacion pedida (dedupe ruta/clic)

  useEffect(() => {
    api.animationsIndex()
      .then((d) => {
        // Las categorias sin animaciones (las del curso de Manim) no se
        // muestran en esta pestana.
        setIndex({ categories: d.categories.filter((c) => c.count > 0) })
      })
      .catch((err) => setError(err.message))
  }, [])

  const open = async (id) => {
    requestedRef.current = id
    setError('')
    try {
      setAnimation(await api.getAnimation(id))
    } catch (err) {
      setError(err.status === 404 ? 'Animación no encontrada' : err.message)
    }
  }

  // Clic del usuario: abre y refleja la animacion en el hash.
  const openAndRoute = (id) => {
    open(id)
    onRoute?.(id)
  }

  // #/animaciones/<id> (carga inicial o atras/adelante) abre esa animacion;
  // el acordeon sigue solo a la categoria del item abierto.
  useEffect(() => {
    if (!index || !routeId || routeId === requestedRef.current) return
    open(routeId)
  }, [index, routeId]) // eslint-disable-line react-hooks/exhaustive-deps

  const totalCount = index ? index.categories.reduce((n, c) => n + c.count, 0) : 0

  if (error && !index) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">{error}</main>
  }
  if (!index) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">Cargando animaciones…</main>
  }

  const crumb = animation && index.categories.find((c) => animation.id.startsWith(c.slug + '/'))?.name

  return (
    <main className="grid min-h-0 flex-1 grid-rows-[auto_1fr] gap-3 p-3 lg:grid-cols-[300px_1fr] lg:grid-rows-1">
      {/* En movil la columna de categorias se acota a media pantalla (la lista
          scrollea por dentro) para que la vista previa quede al alcance. */}
      <aside className="panel flex max-h-[45dvh] min-h-0 flex-col overflow-hidden lg:max-h-none">
        <CategoryBrowser
          title="Animaciones"
          categories={index.categories}
          itemsOf={(c) => c.animations}
          searchText={(a) => `${a.title} ${a.scene || ''}`}
          activeId={animation?.id}
          onOpen={openAndRoute}
          renderItem={(a) => (
            <>
              <span className="block text-[13px] text-ink">{a.title}</span>
              <span className="block font-mono text-[11px] text-muted">{a.scene || 'sin escena'}</span>
            </>
          )}
        />
      </aside>

      <section className="panel flex min-h-[50dvh] flex-col overflow-hidden lg:min-h-0" aria-label="vista previa">
        {animation ? (
          <>
            <header className="border-b border-line px-4 py-3">
              <p className="font-mono text-[10.5px] uppercase tracking-[0.16em] text-accent">{crumb}</p>
              <h1 className="mt-1 font-display text-xl font-semibold text-ink">{animation.title}</h1>
              <p className="mt-0.5 text-xs text-muted">{animation.scene || 'sin escena detectada'}</p>
            </header>
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
              <span className="font-mono text-[13px] text-ink">{animation.id}.py</span>
              <Button variant="primary" size="sm" onClick={() => onOpenInStudio(animation.script)}>
                Abrir en el Estudio
              </Button>
            </div>
            <CodeMirror
              value={animation.script}
              extensions={[python()]}
              theme="dark"
              editable={false}
              height="100%"
              className="editor min-h-0 flex-1 overflow-auto text-[13px]"
              basicSetup={{ foldGutter: false, highlightActiveLine: false }}
            />
          </>
        ) : (
          <div className="grid flex-1 place-items-center p-6 text-center">
            <p className="text-[13px] text-muted">
              Elige una animación. {totalCount} animaciones en {index.categories.length} categorías.
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
