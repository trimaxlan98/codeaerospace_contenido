// Biblioteca de animaciones: categorias + lista + vista previa del script,
// con un boton para abrirlo en el Estudio y renderizarlo. Desde aqui tambien
// se anaden secciones nuevas y animaciones a una seccion (persisten como
// archivos en studio/content/, igual que el contenido versionado).

import { useCallback, useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { api } from './api.js'
import CategoryBrowser from './components/CategoryBrowser.jsx'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'

const SCRIPT_TEMPLATE = `from manim import *


class MiEscena(Scene):
    def construct(self):
        titulo = Text("Nueva animación", font_size=36)
        self.play(FadeIn(titulo))
        self.wait(1)
`

export default function Animations({ onOpenInStudio, routeId, onRoute }) {
  const [index, setIndex] = useState(null)
  const [error, setError] = useState('')
  const [animation, setAnimation] = useState(null) // {id, title, scene, script}
  const [newSectionOpen, setNewSectionOpen] = useState(false)
  const [addTarget, setAddTarget] = useState(null) // categoria destino del alta
  const requestedRef = useRef(null) // ultima animacion pedida (dedupe ruta/clic)

  const loadIndex = useCallback(() => (
    api.animationsIndex()
      .then((d) => {
        // Se muestran las categorias con animaciones o con directorio propio
        // (p.ej. secciones recien creadas, aun vacias); las solo-lecciones
        // del curso de Manim quedan fuera de esta pestana.
        setIndex({ categories: d.categories.filter((c) => c.count > 0 || c.has_dir) })
      })
      .catch((err) => setError(err.message))
  ), [])

  useEffect(() => { loadIndex() }, [loadIndex])

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
          onAddCategory={() => setNewSectionOpen(true)}
          onAddItem={(c) => setAddTarget(c)}
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

      <NewSectionDialog open={newSectionOpen} onOpenChange={setNewSectionOpen}
        onCreated={() => { setNewSectionOpen(false); loadIndex() }} />
      <AddAnimationDialog category={addTarget} onOpenChange={(v) => { if (!v) setAddTarget(null) }}
        onCreated={(a) => { setAddTarget(null); loadIndex(); openAndRoute(a.id) }} />
    </main>
  )
}

// ── alta de seccion ─────────────────────────────────────────────────────────

function NewSectionDialog({ open, onOpenChange, onCreated }) {
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) { setName(''); setError('') }
  }, [open])

  const submit = async (e) => {
    e.preventDefault()
    if (!name.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      onCreated(await api.createAnimationCategory(name.trim()))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="w-[min(440px,94vw)] p-0">
          <form onSubmit={submit} className="flex flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Nueva sección</DialogTitle>
            </div>
            <div className="flex flex-col gap-3 p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Nombre</span>
                <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus required
                  maxLength={80} placeholder="p. ej. Propulsión Iónica" />
              </label>
              <p className="text-[12px] text-muted">
                La sección aparece en Animaciones y agrupa las animaciones que añadas.
              </p>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy || !name.trim()}>Crear</Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}

// ── alta de animacion en una seccion ────────────────────────────────────────

function AddAnimationDialog({ category, onOpenChange, onCreated }) {
  const open = Boolean(category)
  const [title, setTitle] = useState('')
  const [script, setScript] = useState(SCRIPT_TEMPLATE)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) { setTitle(''); setScript(SCRIPT_TEMPLATE); setError('') }
  }, [open])

  const submit = async (e) => {
    e.preventDefault()
    if (!title.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      onCreated(await api.createAnimation({
        category: category.slug, title: title.trim(), script,
      }))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <form onSubmit={submit} className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">
                Añadir animación · {category.name}
              </DialogTitle>
            </div>
            <div className="flex min-h-0 flex-col gap-3 overflow-y-auto p-4">
              <label className="flex flex-col gap-1">
                <span className="eyebrow">Título</span>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} autoFocus required
                  maxLength={120} placeholder="p. ej. Transferencia de Hohmann" />
              </label>
              <div className="flex min-h-0 flex-col gap-1">
                <span className="eyebrow">Script (debe definir al menos una escena)</span>
                <CodeMirror
                  value={script}
                  onChange={setScript}
                  extensions={[python()]}
                  theme="dark"
                  height="260px"
                  className="editor overflow-hidden rounded-md border border-line text-[13px]"
                  basicSetup={{ foldGutter: false, highlightActiveLine: false }}
                />
              </div>
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>
            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy || !title.trim()}>Añadir</Button>
            </div>
          </form>
        </DialogContent>
      )}
    </Dialog>
  )
}
