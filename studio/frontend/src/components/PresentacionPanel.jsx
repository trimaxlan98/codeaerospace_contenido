// La presentación: los renders del proyecto convertidos en un .pptx
// que el ponente abre y presenta.
//
// El panel es pequeño porque la decisión real es UNA: **GIF o vídeo**. Un GIF
// arranca solo al entrar al slide en todas las versiones de PowerPoint, sin
// XML de por medio; un vídeo pesa menos pero su autoplay depende del árbol
// <p:timing> del OOXML, y eso hay que verificarlo una vez en el equipo de
// quien presenta. Por eso el defecto es GIF y el vídeo se explica al elegirlo.
//
// Lo demás que enseña —la lista de slides con su etiqueta y su duración— no es
// decoración: es el guion del ponente. Saber que el paso 3 dura 4 s y se llama
// «La cifra» es lo que permite ensayar.

import { useCallback, useEffect, useState } from 'react'
import { Download, Presentation, Square, Trash2 } from 'lucide-react'
import { api, presentacionDeckUrl } from '../api.js'
import { Button } from './ui/button.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

// Etiqueta y tono de cada estado. Los ids vienen de app/presentaciones.py.
export const PRESENTACION_META = {
  sin_clips: { label: 'sin escenas', tone: 'text-muted' },
  faltan_renders: { label: 'sin renders', tone: 'text-muted' },
  sin_armar: { label: 'sin armar', tone: 'text-muted' },
  desactualizado: { label: 'desactualizado', tone: 'text-warn' },
  al_dia: { label: 'al día', tone: 'text-ok' },
  armando: { label: 'armando…', tone: 'text-accent' },
}

const DECK_LABEL = {
  gif: 'GIF — arranca solo en cualquier PowerPoint',
  video: 'Vídeo — pesa menos, verifica el autoplay',
}

function fmtDur(s) {
  if (!s && s !== 0) return '—'
  const m = Math.floor(s / 60)
  if (m === 0) return `${s.toFixed(1)} s`
  return `${m} min ${String(Math.round(s % 60)).padStart(2, '0')} s`
}

function fmtMB(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

// Los slides, en orden. Cada uno es un clic del ponente; la barra da su peso
// relativo en el tiempo, que es lo que se ensaya.
function Slides({ fragmentos }) {
  const total = fragmentos.reduce((a, f) => a + (f.duracion || 0), 0)
  if (!total) return null
  return (
    <ol className="space-y-1">
      {fragmentos.map((f, i) => (
        <li key={f.nombre || i} className="flex items-center gap-2 text-xs">
          <span className="w-6 shrink-0 text-right font-mono text-[10.5px] text-faint">
            {i + 1}
          </span>
          <span className="min-w-0 flex-1 truncate text-ink/80" title={f.escena || ''}>
            {f.etiqueta || f.nombre}
          </span>
          <span className="h-1.5 shrink-0 rounded-full bg-accent/60"
            style={{ width: `${Math.max(((f.duracion || 0) / total) * 40, 2)}%` }} />
          <span className="w-12 shrink-0 text-right font-mono text-[10.5px] text-faint">
            {fmtDur(f.duracion)}
          </span>
        </li>
      ))}
    </ol>
  )
}

export default function PresentacionPanel({ projectId }) {
  const [estado, setEstado] = useState(null)
  const [error, setError] = useState('')
  const [deck, setDeck] = useState('gif')
  const [bucle, setBucle] = useState(false)

  const load = useCallback(() => {
    api.getPresentacion(projectId).then((e) => {
      setEstado(e)
      if (e?.opciones) {
        setDeck(e.opciones.deck || 'gif')
        setBucle(Boolean(e.opciones.bucle))
      }
    }).catch(() => setEstado(null))
  }, [projectId])

  useEffect(() => { load() }, [load])

  // Mientras arma se sondea; el resultado durable vive en presentacion.json.
  const armando = estado?.estado === 'armando'
  useEffect(() => {
    if (!armando) return
    const t = setInterval(load, 4000)
    return () => clearInterval(t)
  }, [armando, load])

  const armar = async () => {
    setError('')
    try {
      await api.armarPresentacion(projectId, { deck, bucle })
      load()
    } catch (err) { setError(err.message) }
  }

  const cancelar = async () => {
    try { await api.cancelarPresentacion(projectId) } catch (err) { setError(err.message) }
    load()
  }

  const borrar = async () => {
    try { await api.borrarPresentacion(projectId) } catch (err) { setError(err.message) }
    load()
  }

  if (!estado) return null

  const meta = PRESENTACION_META[estado.estado] || PRESENTACION_META.sin_armar
  const informe = estado.informe
  const hayDeck = Boolean(informe) && estado.estado !== 'sin_armar'
  const puedeArmar = estado.escenas > 0 && !armando
  const runError = estado.run?.estado === 'error' ? estado.run.error : ''
  const fragmentos = informe?.fragmentos || []

  return (
    <section className="rounded-lg border border-line bg-surface-2 p-3 space-y-3">
      <header className="flex flex-wrap items-center gap-2">
        <Presentation className="h-4 w-4 text-accent" />
        <h3 className="text-sm font-semibold">El PowerPoint</h3>
        <span className={cn('text-xs', meta.tone)}>{meta.label}</span>
        <span className="text-xs text-muted ml-auto">
          {estado.escenas} escena{estado.escenas === 1 ? '' : 's'}
          {fragmentos.length > 0 ? ` · ${fragmentos.length} slides` : ''}
          {estado.faltan?.length > 0 ? ` · ${estado.faltan.length} sin render` : ''}
        </span>
      </header>

      {estado.problema && !hayDeck && (
        <p className="text-xs text-muted">{estado.problema}</p>
      )}

      <div className="flex flex-wrap items-end gap-2">
        <label className="text-xs text-muted space-y-1">
          <span className="block">Cómo va la animación en el slide</span>
          <Select value={deck} onValueChange={setDeck}>
            <SelectTrigger className="h-8 w-72 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              {(estado.decks || ['gif']).map((d) => (
                <SelectItem key={d} value={d}>{DECK_LABEL[d] || d}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </label>

        <label className="flex items-center gap-1.5 pb-1.5 text-xs text-muted"
          title="Un fragmento de una construcción por pasos debe reproducirse una vez y quedarse congelado: repetirlo detrás de quien habla distrae. Actívalo solo en una presentación decorativa de una sola parte.">
          <input type="checkbox" checked={bucle}
            onChange={(e) => setBucle(e.target.checked)} />
          en bucle
        </label>

        <div className="ml-auto flex items-center gap-2">
          {armando ? (
            <Button variant="ghost" size="sm" onClick={cancelar}>
              <Square className="mr-1 h-3.5 w-3.5" /> Cancelar
            </Button>
          ) : (
            <Button variant="primary" size="sm" onClick={armar} disabled={!puedeArmar}>
              <Presentation className="mr-1 h-3.5 w-3.5" />
              {hayDeck ? 'Volver a armar' : 'Armar el PowerPoint'}
            </Button>
          )}
          {hayDeck && (
            <>
              <Button asChild variant="ghost" size="sm">
                <a href={presentacionDeckUrl(projectId)} download>
                  <Download className="mr-1 h-3.5 w-3.5" /> .pptx
                </a>
              </Button>
              <Button variant="ghost" size="sm" onClick={borrar} title="Borrar el deck">
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </>
          )}
        </div>
      </div>

      {deck === 'video' && (
        <p className="text-xs text-warn">
          El deck de vídeo pesa menos, pero que arranque solo depende del XML de
          PowerPoint: <strong>ábrelo una vez</strong> en el equipo con el que vas
          a presentar. Si no arranca, un clic sobre el slide lo dispara. El deck
          de GIF no depende de nada.
        </p>
      )}

      {estado.faltan?.length > 0 && (
        <p className="text-xs text-muted">
          Sin render vigente (no entran al deck): {estado.faltan.join(', ')}
        </p>
      )}

      {informe?.avisos?.length > 0 && informe.avisos.map((a, i) => (
        <p key={i} className="text-xs text-warn">{a}</p>
      ))}

      {runError && <p className="text-xs text-err">{runError}</p>}
      {error && <p className="text-xs text-err">{error}</p>}

      {hayDeck && (
        <>
          <Slides fragmentos={fragmentos} />
          <p className="font-mono text-[10.5px] text-faint">
            {fragmentos.length} slides · {fmtDur(informe.duracion)} de animación ·
            {' '}{informe.resolucion} · deck {fmtMB(informe.peso_deck)}
            {informe.fondo_usado ? ` · fondo ${informe.fondo_usado}` : ''}
          </p>
        </>
      )}
    </section>
  )
}
