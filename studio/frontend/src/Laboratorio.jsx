// Laboratorio — Python de validación en el sandbox.
//
// La brecha que cierra: **las sondas**. `studio/tools/sonda_*.py` son el
// guardián de cada librería del repo (cada invariante con su contraejemplo, y
// una tabla de cifras medidas) y sólo se podían correr desde una terminal. En
// la app no había forma de «verificar la librería» antes de escribir un clip,
// ni de calcular una cifra con numpy, ni de dibujar un PNG con PIL. El único
// Python que la consola sabía ejecutar era una escena de manim, y sólo para
// producir un mp4.
//
// Decisiones de la vista:
//
//   - **La sonda se corre con un botón, no copiando su código al editor.** Lo
//     que se ejecuta es el archivo del repo montado read-only: si mañana
//     cambia, el botón corre la versión nueva.
//   - **La salida manda sobre el editor.** Lo que importa es el veredicto de
//     la última línea («18 invariantes ok, 0 fallos»), así que el historial
//     lo enseña sin abrir la ejecución.
//   - **`exit 1` no se pinta como avería.** Una sonda con invariantes rotos
//     sale con 1 a propósito: eso es ámbar (resultado), no rojo (fallo).
//   - **Se pregunta, no se escucha.** La ejecución va en segundo plano; la
//     vista consulta cada 1,2 s mientras dura y para en cuanto termina. No
//     hay evento SSE nuevo por una tarea que dura segundos.

import { useCallback, useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import {
  Play, FlaskConical, ShieldCheck, Trash2, Download, FileText, RotateCcw,
} from 'lucide-react'
import { api, labArchivoUrl } from './api.js'
import { Button } from './components/ui/button.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select.jsx'
import { cn } from '@/lib/utils'
import { useEditorTheme } from './themes.js'

const LS_SCRIPT = 'ms_lab_script'
const TIMEOUTS = [60, 120, 300, 600, 900]
const MS_SONDEO = 1200

const ESTADO_META = {
  corriendo: { label: 'corriendo', dot: 'bg-accent', text: 'text-accent' },
  ok: { label: 'ok', dot: 'bg-ok', text: 'text-ok' },
  // Salida distinta de cero: es el RESULTADO del script (una sonda que
  // encuentra fallos sale con 1), no una avería de la consola.
  salida: { label: 'con hallazgos', dot: 'bg-warn', text: 'text-warn' },
  timeout: { label: 'timeout', dot: 'bg-err', text: 'text-err' },
  error: { label: 'error', dot: 'bg-err', text: 'text-err' },
}

function lsGet(key) {
  try { return localStorage.getItem(key) } catch { return null }
}

function lsSet(key, value) {
  try { localStorage.setItem(key, value) } catch { /* no critico */ }
}

function fmtHora(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleTimeString('es', { hour12: false })
}

function fmtBytes(n) {
  if (n == null) return '—'
  if (n >= 1024 * 1024) return `${(n / (1024 * 1024)).toFixed(1)} MB`
  if (n >= 1024) return `${Math.round(n / 1024)} KB`
  return `${n} B`
}

const ES_IMAGEN = /\.(png|jpe?g|svg)$/i
const ES_AUDIO = /\.wav$/i

export default function Laboratorio({ active }) {
  const temaEditor = useEditorTheme()
  const [script, setScript] = useState(() => lsGet(LS_SCRIPT) || '')
  const [timeoutS, setTimeoutS] = useState(120)
  const [plantilla, setPlantilla] = useState('')
  const [sondas, setSondas] = useState([])
  const [historial, setHistorial] = useState([])
  const [actual, setActual] = useState(null)   // detalle de la ejecución abierta
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)
  const sondeoRef = useRef(null)

  const corriendo = actual?.estado === 'corriendo'

  const refrescar = useCallback(async () => {
    try {
      const d = await api.listarLab()
      setHistorial(d.ejecuciones || [])
      if (d.plantilla) setPlantilla(d.plantilla)
      return d
    } catch (err) {
      setError(err.message)
      return null
    }
  }, [])

  // Carga inicial (una sola vez, al visitar la vista: es keep-alive).
  const cargadoRef = useRef(false)
  useEffect(() => {
    if (!active || cargadoRef.current) return
    cargadoRef.current = true
    refrescar().then((d) => {
      // El editor arranca con la plantilla del servidor si no hay trabajo
      // propio guardado: un editor vacío no enseña qué se puede hacer aquí.
      if (d?.plantilla && !lsGet(LS_SCRIPT)) setScript(d.plantilla)
    })
    api.getSondas().then((d) => setSondas(d.sondas || [])).catch(() => {})
  }, [active, refrescar])

  // Guardado local del script con debounce (sobrevive a F5 y a cambiar de
  // vista, igual que el editor del Estudio).
  useEffect(() => {
    const t = setTimeout(() => lsSet(LS_SCRIPT, script), 400)
    return () => clearTimeout(t)
  }, [script])

  // Sondeo mientras hay algo corriendo; se apaga solo al terminar.
  useEffect(() => {
    clearInterval(sondeoRef.current)
    if (!corriendo || !actual?.id) return undefined
    sondeoRef.current = setInterval(async () => {
      try {
        const d = await api.getLab(actual.id)
        setActual(d)
        if (d.estado !== 'corriendo') refrescar()
      } catch {
        clearInterval(sondeoRef.current)
      }
    }, MS_SONDEO)
    return () => clearInterval(sondeoRef.current)
  }, [corriendo, actual?.id, refrescar])

  const lanzar = useCallback(async (fn) => {
    setError('')
    setEnviando(true)
    try {
      const d = await fn()
      setActual(d)
      refrescar()
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }, [refrescar])

  const ejecutar = () => {
    if (!script.trim()) { setError('El script está vacío'); return }
    lanzar(() => api.ejecutarLab({ script, timeout: Number(timeoutS) }))
  }

  const abrir = async (id) => {
    setError('')
    try {
      setActual(await api.getLab(id))
    } catch (err) {
      setError(err.message)
    }
  }

  const borrar = async (id) => {
    setError('')
    try {
      await api.borrarLab(id)
      if (actual?.id === id) setActual(null)
      refrescar()
    } catch (err) {
      setError(err.message)
    }
  }

  const ocupado = enviando || corriendo

  return (
    <main data-view="laboratorio" className="flex flex-1 flex-col gap-3 p-3 lg:min-h-0">
      <div className="flex flex-col gap-3 lg:min-h-0 lg:flex-1 lg:flex-row">
        {/* ── Editor ── */}
        <section className="panel flex h-[52dvh] min-w-0 flex-col overflow-hidden lg:h-auto lg:min-h-0 lg:flex-1"
          aria-label="editor del laboratorio"
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
              e.preventDefault()
              if (!ocupado) ejecutar()
            }
          }}>
          <div className="flex flex-wrap items-center gap-2 border-b border-line px-3 py-2">
            <FlaskConical className="h-4 w-4 text-muted" />
            <span className="font-mono text-[13px] text-ink">script.py</span>
            <span className="hidden items-center gap-1.5 rounded-md border border-line px-2 py-0.5 font-mono text-[10.5px] uppercase tracking-wide text-muted sm:inline-flex"
              title="El script corre en el mismo contenedor que un render: sin red, con el repo de solo lectura y con permiso de escritura solo en su propio directorio.">
              <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-ok" />
              sandbox · sin red
            </span>
            <div className="ml-auto flex flex-wrap items-center gap-2">
              <label className="flex items-center gap-1.5">
                <span className="eyebrow">Timeout</span>
                <Select value={String(timeoutS)} onValueChange={(v) => setTimeoutS(Number(v))}>
                  <SelectTrigger className="h-8 w-[92px]"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {TIMEOUTS.map((t) => <SelectItem key={t} value={String(t)}>{t} s</SelectItem>)}
                  </SelectContent>
                </Select>
              </label>
              {plantilla && (
                <Button size="sm" variant="ghost" onClick={() => setScript(plantilla)}
                  title="Vuelve al ejemplo de partida (numpy + una librería del repo + PIL)">
                  <RotateCcw className="h-4 w-4" /> Plantilla
                </Button>
              )}
              <Button variant="primary" size="sm" onClick={ejecutar} disabled={ocupado}
                title="Ejecuta el script en el contenedor · Ctrl+Enter">
                <Play className="h-4 w-4" />
                {enviando ? 'Enviando…' : corriendo ? 'Corriendo…' : 'Ejecutar'}
              </Button>
            </div>
          </div>

          {error && (
            <p role="alert" className="border-b border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">
              {error}
            </p>
          )}

          <CodeMirror
            value={script}
            onChange={setScript}
            extensions={[python()]}
            theme={temaEditor}
            height="100%"
            className="editor min-h-0 flex-1 overflow-auto text-[13px]"
            basicSetup={{ foldGutter: false, highlightActiveLine: true }}
          />
        </section>

        {/* ── Salida ── */}
        <aside className="flex w-full flex-col gap-3 lg:min-h-0 lg:w-[440px] lg:shrink-0"
          aria-label="salida">
          <Salida ejecucion={actual} />
        </aside>
      </div>

      {/* ── Sondas del repo + historial ── */}
      <div className="flex flex-col gap-3 lg:flex-row">
        <Sondas sondas={sondas} ocupado={ocupado}
          onCorrer={(n) => lanzar(() => api.correrSonda(n))} />
        <Historial filas={historial} actual={actual?.id}
          onAbrir={abrir} onBorrar={borrar} />
      </div>
    </main>
  )
}

function Salida({ ejecucion }) {
  if (!ejecucion) {
    return (
      <div className="panel flex h-[40dvh] flex-col justify-center gap-2 px-4 text-center lg:h-auto lg:min-h-0 lg:flex-1">
        <p className="text-[13px] text-muted">
          Sin ejecuciones todavía. Escribe un script y pulsa Ejecutar, o corre
          una <strong className="font-semibold text-ink">sonda</strong> para
          verificar una librería del repo.
        </p>
      </div>
    )
  }
  const m = ESTADO_META[ejecucion.estado] || ESTADO_META.error
  const salida = [ejecucion.stdout, ejecucion.stderr].filter(Boolean).join('\n')
  return (
    <div className="panel flex h-[45dvh] flex-col overflow-hidden lg:h-auto lg:min-h-0 lg:flex-1">
      <div className="flex flex-wrap items-center gap-2 border-b border-line px-3 py-2">
        <span className={cn('h-2 w-2 shrink-0 rounded-full', m.dot,
          ejecucion.estado === 'corriendo' && 'animate-pulse')} />
        <span className="eyebrow truncate">{ejecucion.titulo}</span>
        <span className={cn('font-mono text-[10px] uppercase tracking-wide', m.text)}>
          {m.label}
        </span>
        <span className="ml-auto font-mono text-[11px] text-faint">
          {ejecucion.code != null && `exit ${ejecucion.code}`}
          {ejecucion.duracion_s != null && ` · ${ejecucion.duracion_s}s`}
        </span>
      </div>
      <pre className="m-0 min-h-0 flex-1 overflow-auto whitespace-pre-wrap break-words bg-canvas px-3 py-2.5 font-mono text-[11.5px] leading-relaxed text-code-ink">
        {salida || (ejecucion.estado === 'corriendo'
          ? 'Corriendo en el contenedor…'
          : 'Sin salida.')}
      </pre>
      {ejecucion.archivos?.length > 0 && (
        <div className="shrink-0 border-t border-line p-2.5">
          <span className="eyebrow">Archivos producidos</span>
          <div className="mt-1.5 grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-2">
            {ejecucion.archivos.map((f) => (
              <Producido key={f.nombre} labId={ejecucion.id} archivo={f} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/** Un archivo que dejó el script. Las imágenes se ven aquí mismo (el motivo
 *  de dibujar un PNG es mirarlo); el resto se descarga. */
function Producido({ labId, archivo }) {
  const url = labArchivoUrl(labId, archivo.nombre)
  if (ES_IMAGEN.test(archivo.nombre)) {
    return (
      <a href={url} download={archivo.nombre} title={`${archivo.nombre} · ${fmtBytes(archivo.bytes)}`}
        className="block overflow-hidden rounded-md border border-line bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
        <img src={url} alt={archivo.nombre} loading="lazy" className="block w-full" />
        <span className="block truncate px-1.5 py-1 font-mono text-[10.5px] text-muted">
          {archivo.nombre}
        </span>
      </a>
    )
  }
  if (ES_AUDIO.test(archivo.nombre)) {
    return (
      <div className="flex flex-col gap-1 rounded-md border border-line p-1.5">
        <span className="truncate font-mono text-[10.5px] text-muted">{archivo.nombre}</span>
        <audio controls preload="none" src={url} className="w-full" />
      </div>
    )
  }
  return (
    <a href={url} download={archivo.nombre}
      className="flex items-center gap-1.5 rounded-md border border-line px-2 py-1.5 text-[11.5px] text-muted transition-colors hover:border-line-strong hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
      <FileText className="h-3.5 w-3.5 shrink-0" />
      <span className="truncate">{archivo.nombre}</span>
      <span className="ml-auto shrink-0 font-mono text-[10px] text-faint">
        {fmtBytes(archivo.bytes)}
      </span>
    </a>
  )
}

function Sondas({ sondas, ocupado, onCorrer }) {
  return (
    <section className="panel flex min-w-0 flex-1 flex-col overflow-hidden" aria-label="sondas">
      <div className="flex items-center gap-2 border-b border-line px-3 py-1.5">
        <ShieldCheck className="h-3.5 w-3.5 text-muted" />
        <span className="eyebrow">Sondas del repo</span>
        <span className="font-mono text-[11px] text-faint">{sondas.length}</span>
        <span className="ml-auto hidden text-[11.5px] text-faint sm:inline">
          verifican las librerías: cada invariante con su contraejemplo
        </span>
      </div>
      {sondas.length === 0 ? (
        <p className="px-3 py-3 text-[13px] text-muted">
          No se encontró ninguna <code className="font-mono">sonda_*.py</code>.
        </p>
      ) : (
        <div className="max-h-[220px] overflow-y-auto">
          {sondas.map((s) => (
            <div key={s.nombre}
              className="flex items-center gap-2 border-b border-line/60 px-3 py-1.5 last:border-b-0">
              <span className="shrink-0 font-mono text-[12.5px] text-ink">{s.nombre}</span>
              <span className="truncate text-[11.5px] text-muted" title={s.que}>{s.que}</span>
              <Button size="xs" variant="default" className="ml-auto shrink-0"
                disabled={ocupado} onClick={() => onCorrer(s.nombre)}
                title={`Corre studio/tools/${s.archivo} tal cual, en el contenedor`}>
                <Play className="h-3 w-3" /> Correr
              </Button>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

function Historial({ filas, actual, onAbrir, onBorrar }) {
  return (
    <section className="panel flex min-w-0 flex-1 flex-col overflow-hidden" aria-label="historial">
      <div className="flex items-center gap-2 border-b border-line px-3 py-1.5">
        <span className="eyebrow">Ejecuciones</span>
        <span className="font-mono text-[11px] text-faint">{filas.length}</span>
      </div>
      {filas.length === 0 ? (
        <p className="px-3 py-3 text-[13px] text-muted">Sin ejecuciones todavía.</p>
      ) : (
        <div className="max-h-[220px] overflow-y-auto">
          {filas.map((f) => {
            const m = ESTADO_META[f.estado] || ESTADO_META.error
            return (
              <div key={f.id}
                className={cn('flex items-center gap-2 border-b border-line/60 px-3 py-1.5 last:border-b-0',
                  actual === f.id && 'bg-surface-2')}>
                <span className={cn('h-2 w-2 shrink-0 rounded-full', m.dot)} />
                <button type="button" onClick={() => onAbrir(f.id)}
                  className="flex min-w-0 flex-1 items-center gap-2 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                  <span className="shrink-0 font-mono text-[11px] text-faint">{fmtHora(f.creado)}</span>
                  <span className="shrink-0 text-[12.5px] text-ink">{f.titulo}</span>
                  {/* El veredicto de la última línea: en una sonda es
                      justamente lo que se quería saber. */}
                  <span className="truncate font-mono text-[11px] text-muted" title={f.resumen}>
                    {f.resumen}
                  </span>
                </button>
                {f.n_archivos > 0 && (
                  <span className="shrink-0 font-mono text-[10.5px] text-faint"
                    title={`${f.n_archivos} archivo(s) producido(s)`}>
                    <Download className="inline h-3 w-3" /> {f.n_archivos}
                  </span>
                )}
                <button type="button" onClick={() => onBorrar(f.id)}
                  aria-label={`borrar ejecución ${f.titulo}`}
                  className="shrink-0 rounded p-1 text-muted transition-colors hover:bg-err/10 hover:text-err focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
