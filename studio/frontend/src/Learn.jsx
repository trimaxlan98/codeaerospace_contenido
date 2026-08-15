// Aprender — teoria y ejemplos ejecutables en una sola seccion (encargo 7).
//
// Hasta el sprint 4 esto eran DOS pestañas, "Aprender" y "Animaciones", que
// leian el mismo indice del backend (`studio/content/lessons/categories.yaml`)
// y se ignoraban entre si: buscar "orbita" en Aprender no encontraba la
// animacion de orbita, y para pasar de la teoria al ejemplo habia que cambiar
// de pestaña y volver a buscar. El backend siempre las trato como lo mismo —
// el id de una animacion es 1:1 el de su leccion (`animations.py`) — asi que
// la separacion solo existia en la interfaz.
//
// Aqui hay un unico indice con dos grupos (curso de Manim / animaciones por
// dominio), una sola busqueda global, y un lector que enseña lo que el item
// tenga: markdown, script, o los dos con un conmutador si algun dia coinciden.
//
// Rutas: `#/aprender/<id>` abre cualquiera de los dos. `#/animaciones/<id>`
// sigue funcionando (router.js lo mapea a esta vista) para no romper enlaces.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { Play, Plus } from 'lucide-react'
import { api } from './api.js'
import { renderMarkdown } from './markdown.js'
import CategoryBrowser from './components/CategoryBrowser.jsx'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './components/ui/dialog.jsx'
import { cn } from '@/lib/utils'
import 'katex/dist/katex.min.css'

const READ_KEY = 'ms_lessons_read'
const LEVEL_LABEL = { intro: 'intro', medio: 'medio', avanzado: 'avanzado' }

const SCRIPT_TEMPLATE = `from manim import *


class MiEscena(Scene):
    def construct(self):
        titulo = Text("Nueva animación", font_size=36)
        self.play(FadeIn(titulo))
        self.wait(1)
`

function readSet() {
  try { return new Set(JSON.parse(localStorage.getItem(READ_KEY)) || []) }
  catch { return new Set() }
}

export default function Learn({ routeId, onRoute, onOpenInStudio, active = true }) {
  const [lessonIndex, setLessonIndex] = useState(null)
  const [animIndex, setAnimIndex] = useState(null)
  const [error, setError] = useState('')
  const [item, setItem] = useState(null) // {kind:'lesson'|'animation', ...}
  const [read, setRead] = useState(readSet)
  const [progress, setProgress] = useState(0)
  const [newSectionOpen, setNewSectionOpen] = useState(false)
  const [addTarget, setAddTarget] = useState(null)
  const readerRef = useRef(null)
  const endRef = useRef(null)   // pie de la leccion: al verlo se marca leida
  const scrollRef = useRef(0)   // scroll del lector, para restaurarlo al volver
  const requestedRef = useRef(null)

  const loadIndexes = useCallback(() => {
    Promise.all([api.lessonsIndex(), api.animationsIndex()])
      .then(([l, a]) => {
        // Categorias con leccion / con animacion (o con directorio propio: las
        // secciones recien creadas desde aqui aun estan vacias).
        setLessonIndex(l.categories.filter((c) => c.count > 0))
        setAnimIndex(a.categories.filter((c) => c.count > 0 || c.has_dir))
      })
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => { loadIndexes() }, [loadIndexes])

  const markRead = useCallback((id) => {
    setRead((prev) => {
      if (prev.has(id)) return prev
      const next = new Set(prev).add(id)
      try { localStorage.setItem(READ_KEY, JSON.stringify([...next])) } catch { /* no critico */ }
      return next
    })
  }, [])

  // Un id puede existir como leccion, como animacion o (por diseño del
  // backend) como las dos. Se pide lo que el indice dice que hay; si hay
  // ambas, el lector ofrece el conmutador.
  const open = useCallback(async (id) => {
    requestedRef.current = id
    setError('')
    const inLessons = (lessonIndex || []).some((c) => c.lessons.some((l) => l.id === id))
    const inAnims = (animIndex || []).some((c) => c.animations.some((a) => a.id === id))
    try {
      const [lesson, animation] = await Promise.all([
        inLessons ? api.getLesson(id) : Promise.resolve(null),
        inAnims ? api.getAnimation(id) : Promise.resolve(null),
      ])
      if (!lesson && !animation) throw Object.assign(new Error('No encontrado'), { status: 404 })
      setItem({ id, lesson, animation, kind: lesson ? 'lesson' : 'animation' })
      setProgress(0)
      scrollRef.current = 0
      readerRef.current?.scrollTo(0, 0)
    } catch (err) {
      setError(err.status === 404 ? 'No se encontró ese contenido' : err.message)
    }
  }, [lessonIndex, animIndex])

  const openAndRoute = (id) => { open(id); onRoute?.(id) }

  // Deep-link o atras/adelante: abre ese item una sola vez.
  useEffect(() => {
    if (!lessonIndex || !animIndex || !routeId || routeId === requestedRef.current) return
    open(routeId)
  }, [lessonIndex, animIndex, routeId]) // eslint-disable-line react-hooks/exhaustive-deps

  // Leida al TERMINARLA (no al abrirla): cuando el pie entra en pantalla.
  useEffect(() => {
    if (item?.kind !== 'lesson' || !endRef.current) return
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) markRead(item.id)
    }, { threshold: 0.6 })
    io.observe(endRef.current)
    return () => io.disconnect()
  }, [item, markRead])

  // La vista vive oculta (keep-alive) y display:none pierde el scroll.
  useEffect(() => {
    if (active && readerRef.current) readerRef.current.scrollTop = scrollRef.current
  }, [active])

  const onScroll = (e) => {
    const el = e.target
    const max = el.scrollHeight - el.clientHeight
    scrollRef.current = el.scrollTop
    setProgress(max > 0 ? Math.min(100, (el.scrollTop / max) * 100) : 100)
  }

  const groups = useMemo(() => ([
    {
      id: 'curso',
      label: 'Curso de Manim',
      categories: lessonIndex || [],
    },
    {
      id: 'animaciones',
      label: 'Animaciones por dominio',
      categories: animIndex || [],
      onAddCategory: () => setNewSectionOpen(true),
      addItemLabel: 'Añadir animación',
    },
  ]), [lessonIndex, animIndex])

  const itemsOf = useCallback((c) => (
    // La misma categoria nunca esta en los dos grupos hoy, pero si lo
    // estuviera cada grupo aporta su lista y no se mezclan.
    c.lessons ? c.lessons.map((l) => ({ ...l, kind: 'lesson' }))
      : (c.animations || []).map((a) => ({ ...a, kind: 'animation' }))
  ), [])

  if (error && !lessonIndex) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">{error}</main>
  }
  if (!lessonIndex || !animIndex) {
    return <main className="grid min-h-0 flex-1 place-items-center p-6 text-[13px] text-muted">Cargando biblioteca…</main>
  }

  const totalLessons = lessonIndex.reduce((n, c) => n + c.count, 0)
  const totalAnims = animIndex.reduce((n, c) => n + c.count, 0)

  return (
    <main data-view="learn"
      className="grid min-h-0 flex-1 grid-rows-[auto_1fr] gap-3 p-3 lg:grid-cols-[300px_1fr] lg:grid-rows-1">
      {/* En movil la columna del indice se acota a media pantalla (scrollea por
          dentro) para que el lector quede al alcance. */}
      <aside className="panel flex max-h-[45dvh] min-h-0 flex-col overflow-hidden lg:max-h-none">
        <CategoryBrowser
          title="Aprender"
          groups={groups}
          itemsOf={itemsOf}
          searchText={(it) => (it.kind === 'lesson'
            ? `${it.title} ${(it.tags || []).join(' ')}`
            : `${it.title} ${it.scene || ''}`)}
          activeId={item?.id}
          onOpen={openAndRoute}
          onAddItem={(c) => setAddTarget(c)}
          renderItem={(it) => (it.kind === 'lesson'
            ? (
              <span className="grid grid-cols-[10px_1fr] gap-x-2.5">
                <span aria-label={read.has(it.id) ? 'leída' : 'no leída'}
                  className={cn('mt-[5px] h-[7px] w-[7px] rounded-full border',
                    read.has(it.id) ? 'border-ok bg-ok' : 'border-muted')} />
                <span className="text-[13px] text-ink">{it.title}</span>
                <span className="col-start-2 font-mono text-[11px] text-muted">
                  {LEVEL_LABEL[it.level] || it.level} · {it.minutes} min
                </span>
              </span>
            ) : (
              <>
                <span className="block text-[13px] text-ink">{it.title}</span>
                <span className="block font-mono text-[11px] text-muted">{it.scene || 'sin escena'}</span>
              </>
            ))}
        />
      </aside>

      <section className="panel relative flex min-h-[50dvh] flex-col overflow-hidden lg:min-h-0" aria-label="lector">
        {item ? (
          <Reader item={item} index={{ lessons: lessonIndex, anims: animIndex }}
            progress={progress} onScroll={onScroll} readerRef={readerRef} endRef={endRef}
            onOpenItem={openAndRoute} onOpenInStudio={onOpenInStudio}
            onKind={(kind) => setItem((p) => ({ ...p, kind }))} />
        ) : (
          <div className="grid flex-1 place-items-center p-6 text-center">
            <p className="max-w-[46ch] text-[13px] text-muted">
              Elige una lección o una animación. {totalLessons} lecciones del curso de
              Manim y {totalAnims} animaciones por dominio, con una sola búsqueda
              para las dos cosas.
            </p>
          </div>
        )}
        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      <NewSectionDialog open={newSectionOpen} onOpenChange={setNewSectionOpen}
        onCreated={() => { setNewSectionOpen(false); loadIndexes() }} />
      <AddAnimationDialog category={addTarget} onOpenChange={(v) => { if (!v) setAddTarget(null) }}
        onCreated={(a) => { setAddTarget(null); loadIndexes(); openAndRoute(a.id) }} />
    </main>
  )
}

// ── lector ──────────────────────────────────────────────────────────────────

function Reader({ item, index, progress, onScroll, readerRef, endRef, onOpenItem,
  onOpenInStudio, onKind }) {
  const { lesson, animation, kind } = item
  const both = Boolean(lesson && animation)
  const showing = kind === 'animation' && animation ? 'animation' : 'lesson'

  const cat = (showing === 'lesson' ? index.lessons : index.anims)
    .find((c) => item.id.startsWith(c.slug + '/'))

  if (showing === 'animation') {
    return (
      <>
        <header className="border-b border-line px-4 py-3">
          <p className="font-mono text-[10.5px] uppercase tracking-[0.16em] text-accent">{cat?.name}</p>
          <h1 className="mt-1 font-display text-xl font-semibold text-ink">{animation.title}</h1>
          <p className="mt-0.5 text-xs text-muted">{animation.scene || 'sin escena detectada'}</p>
        </header>
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="font-mono text-[13px] text-ink">{animation.id}.py</span>
          <div className="flex items-center gap-1.5">
            {both && <KindToggle kind={kind} onKind={onKind} />}
            <Button variant="primary" size="sm" onClick={() => onOpenInStudio(animation.script)}>
              <Play className="h-3.5 w-3.5" /> Abrir en el Estudio
            </Button>
          </div>
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
    )
  }

  const list = cat?.lessons || []
  const i = list.findIndex((l) => l.id === lesson.id)
  const prev = i > 0 ? list[i - 1] : null
  const next = i >= 0 && i < list.length - 1 ? list[i + 1] : null

  return (
    <>
      <div className="absolute inset-x-0 top-0 z-[2] h-0.5 bg-line" aria-hidden="true">
        <div className="h-full bg-accent transition-[width] duration-100" style={{ width: `${progress}%` }} />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-8 py-7" onScroll={onScroll} ref={readerRef}>
        <header className="mx-auto mb-5 max-w-[70ch]">
          <p className="font-mono text-[10.5px] uppercase tracking-[0.16em] text-accent">{cat?.name}</p>
          <div className="mt-1.5 flex flex-wrap items-center gap-3">
            <h1 className="font-display text-[26px] font-semibold text-ink">{lesson.title}</h1>
            {both && <KindToggle kind={kind} onKind={onKind} />}
          </div>
          <p className="mt-1 text-xs text-muted">
            {LEVEL_LABEL[lesson.level] || lesson.level} · {lesson.minutes} min
            {lesson.tags.length > 0 && <> · {lesson.tags.join(' · ')}</>}
          </p>
        </header>
        <LessonBody markdown={lesson.markdown} />
        <footer ref={endRef} className="mx-auto mt-8 flex max-w-[70ch] justify-between gap-2.5">
          {prev ? (
            <Button variant="default" onClick={() => onOpenItem(prev.id)}>← {prev.title}</Button>
          ) : <span />}
          {next && (
            <Button variant="primary" onClick={() => onOpenItem(next.id)}>{next.title} →</Button>
          )}
        </footer>
      </div>
    </>
  )
}

/** Conmutador teoria/ejemplo, solo cuando el id tiene las dos cosas. */
function KindToggle({ kind, onKind }) {
  return (
    <div role="radiogroup" aria-label="qué mostrar"
      className="flex rounded-md border border-line bg-canvas p-0.5">
      {[['lesson', 'Lección'], ['animation', 'Animación']].map(([id, label]) => (
        <button key={id} type="button" role="radio" aria-checked={kind === id}
          onClick={() => onKind(id)}
          className={cn(
            'rounded-[5px] px-2.5 py-1 text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
            kind === id ? 'bg-surface-2 text-accent shadow-sm' : 'text-muted hover:text-ink',
          )}>
          {label}
        </button>
      ))}
    </div>
  )
}

function LessonBody({ markdown }) {
  const html = useMemo(() => renderMarkdown(markdown), [markdown])
  return <article className="reader" dangerouslySetInnerHTML={{ __html: html }} />
}

// ── alta de seccion / animacion (se conservan del antiguo Animaciones) ───────

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
                La sección agrupa animaciones por dominio dentro de Aprender.
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
