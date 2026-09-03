// Los fotogramas de un render: la hoja de contactos y la figura suelta.
//
// Hasta el sprint R3b, el único resultado de un render en la app era el mp4.
// En la terminal el bucle es otro: `render_local.py --frames 8` deja los PNG
// y **se miran uno a uno** antes de dar un clip por bueno —la regla dura del
// proyecto es que nada quede encimado, y eso no lo dice ningún número—; y
// cuando una figura tiene que entrar en la tesis se saca un `ffmpeg -ss` a
// mano. Las dos cosas viven aquí, y las usan el Estudio y Renders.
//
// Dos decisiones:
//
//   - **El último fotograma va aparte y destacado.** Es el que cierra la
//     pieza (y en un vertical, el que empalma con la siguiente): mezclado en
//     la rejilla se revisa como uno más y es el que más se rompe.
//   - **La hoja no se recalcula.** El mp4 de un job es inmutable, así que el
//     backend devuelve la que ya está en disco. Cambiar el número de
//     fotogramas sí lanza el contenedor, y se dice en la interfaz.

import { useCallback, useEffect, useState } from 'react'
import { Grid2x2, Download, Camera, RefreshCw } from 'lucide-react'
import { api } from '../api.js'
import { Button } from './ui/button.jsx'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

// Cuántos fotogramas ofrece la interfaz. El tope duro (24) lo valida el
// backend y el runner; aquí van los que se revisan de una mirada.
export const CUANTOS = [4, 6, 8, 12, 16]
// Anchos de figura. 1920 es la pantalla, 2560 una lámina, 3840 la impresión
// a doble columna de un paper.
const ANCHOS = [1920, 2560, 3840]

function fmtSeg(t) {
  if (t == null) return '—'
  return `${Number(t).toFixed(2)} s`
}

/** Hoja de contactos de un job terminado. */
export default function HojaContactos({ jobId, escena = 'render', abierta = false }) {
  const [n, setN] = useState(8)
  const [hoja, setHoja] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  const [zoom, setZoom] = useState(null) // {url, t} del fotograma ampliado
  const [visible, setVisible] = useState(abierta)

  // Cambiar de job descarta la hoja anterior: si no, la rejilla enseñaría los
  // fotogramas de otro render mientras llega la nueva.
  useEffect(() => { setHoja(null); setError(''); setZoom(null) }, [jobId])

  const pedir = useCallback(async (cuantos) => {
    setCargando(true)
    setError('')
    try {
      setHoja(await api.hojaContactos(jobId, cuantos))
    } catch (err) {
      setError(err.message)
    } finally {
      setCargando(false)
    }
  }, [jobId])

  const abrir = () => {
    setVisible(true)
    if (!hoja) pedir(n)
  }

  if (!visible) {
    return (
      <Button size="xs" variant="default" onClick={abrir}
        title="Extrae fotogramas equiespaciados y el último real, para revisarlos uno a uno">
        <Grid2x2 className="h-3.5 w-3.5" /> Hoja de contactos
      </Button>
    )
  }

  return (
    <div className="flex w-full flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <span className="eyebrow">Hoja de contactos</span>
        {/* `whitespace-nowrap`: el rail del Estudio mide 440 px y «8 fotos»
            partia en dos lineas dentro del disparador, que crecia y se comia
            la fila de arriba. */}
        <Select value={String(n)}
          onValueChange={(v) => { setN(Number(v)); pedir(Number(v)) }}>
          <SelectTrigger className="h-7 w-[104px] shrink-0 whitespace-nowrap"
            aria-label="cuántos fotogramas">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {CUANTOS.map((c) => (
              <SelectItem key={c} value={String(c)}>{c} fotos</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {hoja && (
          <span className="font-mono text-[11px] text-faint">
            {fmtSeg(hoja.duracion)} · {hoja.final?.ancho}×{hoja.final?.alto}
            {hoja.recalculada === false && ' · ya extraída'}
          </span>
        )}
        <Button size="xs" variant="ghost" className="ml-auto"
          onClick={() => pedir(n)} disabled={cargando}
          title="vuelve a extraerlos (el vídeo no cambia, pero el directorio pudo limpiarse)">
          <RefreshCw className={cn('h-3.5 w-3.5', cargando && 'animate-spin')} />
          {cargando ? 'Extrayendo…' : 'Rehacer'}
        </Button>
      </div>

      {error && (
        <p role="alert" className="rounded-md bg-warn/10 px-2.5 py-1.5 text-[12.5px] text-warn">
          {error}
        </p>
      )}

      {cargando && !hoja && (
        <p className="text-[12.5px] text-muted">Extrayendo fotogramas en el contenedor…</p>
      )}

      {hoja && (
        <>
          <div className="grid grid-cols-[repeat(auto-fill,minmax(104px,1fr))] gap-1.5">
            {hoja.frames.map((f) => (
              <Miniatura key={f.archivo} f={f} escena={escena}
                onZoom={() => setZoom(f)} />
            ))}
          </div>
          {hoja.final?.url && (
            <div className="flex flex-col gap-1">
              {/* El último no se mezcla con la tira: es el que cierra la
                  pieza y el que empalma con la siguiente en un vertical. */}
              <span className="eyebrow">Último fotograma real</span>
              <button type="button" onClick={() => setZoom(hoja.final)}
                className="block overflow-hidden rounded-md border border-brand/50 bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
                <img src={hoja.final.url} alt={`último fotograma de ${escena}`}
                  loading="lazy" className="mx-auto block max-h-[220px] w-auto max-w-full" />
              </button>
            </div>
          )}
        </>
      )}

      <Dialog open={!!zoom} onOpenChange={(o) => !o && setZoom(null)}>
        {zoom && (
          <DialogContent className="p-0">
            <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2 pr-12">
              <DialogTitle className="truncate font-mono text-[13px] text-ink">
                {escena} <span className="text-faint">· {fmtSeg(zoom.t)}</span>
              </DialogTitle>
              <a href={zoom.url} download={`${escena}_${zoom.archivo}`}
                className="inline-flex shrink-0 items-center gap-1.5 text-xs text-muted transition-colors hover:text-ink">
                <Download className="h-3.5 w-3.5" /> PNG
              </a>
            </div>
            <img src={zoom.url} alt={`fotograma en ${fmtSeg(zoom.t)}`}
              className="mx-auto block max-h-[78vh] w-auto max-w-full bg-black" />
          </DialogContent>
        )}
      </Dialog>
    </div>
  )
}

function Miniatura({ f, escena, onZoom }) {
  return (
    <button type="button" onClick={onZoom} title={`ampliar (${fmtSeg(f.t)})`}
      className="group relative block overflow-hidden rounded-md border border-line bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
      <img src={f.url} alt={`${escena} en ${fmtSeg(f.t)}`} loading="lazy"
        className="block w-full" />
      {/* El instante va SOBRE la miniatura: revisar la tira es comparar lo
          que se ve con el momento en que pasa. */}
      <span className="absolute bottom-0 left-0 right-0 bg-canvas/80 px-1 py-0.5 text-center font-mono text-[10px] tabular-nums text-muted">
        {fmtSeg(f.t)}
      </span>
    </button>
  )
}

/** «Fotograma → PNG» del instante en curso del <video>, a la resolución
 *  elegida. Es la salida estática para una figura de tesis: el vídeo del job
 *  está a la calidad con que se renderizó, pero el PNG se pide al ancho que
 *  necesita la página. */
export function BotonFotograma({ jobId, escena = 'render', videoRef }) {
  const [ancho, setAncho] = useState(1920)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [ultimo, setUltimo] = useState(null)

  useEffect(() => { setUltimo(null); setError('') }, [jobId])

  const sacar = async () => {
    setBusy(true)
    setError('')
    try {
      // El instante lo manda el reproductor. Al terminar, `currentTime` es
      // exactamente `duration`, y un `-ss` ahí sale con éxito sin escribir
      // nada: el backend lo atiende con `-sseof` (ver hoja_contactos.py).
      const t = Number(videoRef?.current?.currentTime ?? 0)
      const d = await api.fotograma(jobId, Number.isFinite(t) ? t : 0, ancho)
      setUltimo(d)
      // Descarga directa: la figura se quiere en el disco, no en otra pestaña.
      const a = document.createElement('a')
      a.href = d.url
      a.download = `${escena}_${d.archivo}`
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <Button size="xs" variant="default" onClick={sacar} disabled={busy}
        title="Guarda el instante que se está viendo como PNG a la resolución elegida (figura de paper o tesis)">
        <Camera className="h-3.5 w-3.5" /> {busy ? 'Extrayendo…' : 'Fotograma → PNG'}
      </Button>
      <Select value={String(ancho)} onValueChange={(v) => setAncho(Number(v))}>
        <SelectTrigger className="h-7 w-[104px] shrink-0 whitespace-nowrap"
          aria-label="ancho del fotograma">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {ANCHOS.map((a) => <SelectItem key={a} value={String(a)}>{a} px</SelectItem>)}
        </SelectContent>
      </Select>
      {ultimo && !error && (
        <span className="font-mono text-[11px] text-ok">
          {ultimo.ancho}×{ultimo.alto} en {fmtSeg(ultimo.t)}
        </span>
      )}
      {error && <span role="alert" className="text-[11.5px] text-warn">{error}</span>}
    </div>
  )
}
