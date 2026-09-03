// La pelicula del curso: los clips en orden, su narracion y la marca, en un
// solo archivo, montado por la app.
//
// Hasta el sprint E1 esto se hacia fuera: descargar el zip, `unzip`, `sh
// mux.sh`. El panel es deliberadamente pequeno — dos desplegables y un boton —
// porque la decision real es una sola: **corte o transicion**. El corte no
// recodifica (segundos); cualquier otra cosa recodifica la pelicula entera y
// eso hay que decirlo ANTES, no despues de media hora de espera.
//
// Sprint R2: y una cama MUSICAL bajo el curso entero, con el nivel en dB. La
// musica es del curso, no de un clip — por eso vive aqui y no en el dialogo
// de audio de cada pieza —, se sintetiza con la duracion medida del montaje y
// el ensamblador la agacha 9 dB donde suena la voz.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { CheckCircle2, Clapperboard, Download, Film, Play, Ruler, Square, Trash2 } from 'lucide-react'
import { api, peliculaVideoUrl } from '../api.js'
import { cursoDeJob, useCatalogo } from '../catalogo.js'
import MusicaSelector from './MusicaSelector.jsx'
import { Button } from './ui/button.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

// Etiqueta y tono de cada estado. Los ids vienen de app/pelicula.py.
export const PELI_META = {
  sin_clips: { label: 'sin clips', tone: 'text-muted' },
  faltan_renders: { label: 'sin renders', tone: 'text-muted' },
  sin_montar: { label: 'sin montar', tone: 'text-muted' },
  desactualizada: { label: 'desactualizada', tone: 'text-warn' },
  al_dia: { label: 'al día', tone: 'text-ok' },
  montando: { label: 'montando…', tone: 'text-accent' },
}

// Estado de la medicion de la pelicula (app/pelicula.py::estado_verificacion).
const VERIF_META = {
  sin_verificar: { label: 'sin medir', tone: 'text-muted' },
  vieja: { label: 'medición vieja', tone: 'text-warn' },
  pasa: { label: 'medida ✓', tone: 'text-ok' },
  no_pasa: { label: 'no pasa', tone: 'text-err' },
}

const TRANSICION_LABEL = {
  corte: 'Corte seco (no recodifica)',
  fundido: 'Fundido encadenado',
  negro: 'Fundido a negro',
  blanco: 'Fundido a blanco',
  deslizar: 'Deslizar',
  barrido: 'Barrido',
  disolver: 'Disolver',
}

function fmtDur(s) {
  if (!s && s !== 0) return '—'
  const m = Math.floor(s / 60)
  // Por debajo del minuto se enseña un decimal: en una pieza de 8,7 s
  // redondear a «9 s» borra justo lo que se está mirando.
  if (m === 0) return `${s.toFixed(1)} s`
  return `${m} min ${String(Math.round(s % 60)).padStart(2, '0')} s`
}

function fmtMB(bytes) {
  if (!bytes) return '—'
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

// La regleta: una pieza por segmento, ancho proporcional a su duración.
//
// Es lo que convierte una lista de clips en una película que se puede mirar de
// un vistazo: dónde está el clip largo, cuáles llevan voz, dónde caen los
// empalmes. Antes de montar se dibuja con las duraciones que ya conoce la
// narración; después, con las MEDIDAS del informe, que son la verdad.
function Regleta({ piezas, transicion, duracionTransicion, onIr }) {
  const total = piezas.reduce((a, p) => a + (p.duracion || 0), 0)
  if (!total) return null
  // Cada empalme que no es corte se come `d` segundos del total.
  const recorte = transicion === 'corte' ? 0
    : duracionTransicion * Math.max(piezas.length - 1, 0)
  let acumulado = 0
  const conInicio = piezas.map((p) => {
    const inicio = acumulado
    acumulado += (p.duracion || 0) - (transicion === 'corte' ? 0 : duracionTransicion)
    return { ...p, inicio: Math.max(inicio, 0) }
  })

  return (
    <div className="space-y-1">
      <div className="flex h-7 w-full gap-px overflow-hidden rounded border border-line bg-canvas">
        {conInicio.map((p, i) => (
          <button key={i} type="button"
            onClick={() => onIr?.(p.inicio)}
            title={`${p.titulo} · ${fmtDur(p.duracion)}${p.voz ? ' · con voz' : ''}${p.cama ? ' · con cama' : ''}`}
            style={{ width: `${((p.duracion || 0) / total) * 100}%` }}
            className={cn(
              'min-w-[2px] transition-opacity hover:opacity-70',
              p.marca ? 'bg-accent'
                : p.voz ? 'bg-ink/70'
                  : 'bg-muted/40')} />
        ))}
      </div>
      <p className="font-mono text-[10.5px] text-faint">
        {piezas.length} piezas · {fmtDur(total - recorte)}
        {recorte > 0 && ` (los ${piezas.length - 1} empalmes se comen ${recorte.toFixed(1)} s)`}
        {' · '}
        <span className="text-ink/70">■</span> con voz{' '}
        <span className="text-accent">■</span> marca{' '}
        <span className="text-muted">■</span> mudo
      </p>
    </div>
  )
}

export default function PeliculaPanel({ projectId, projectName, jobs, clips, duraciones, narrarConVoz }) {
  const videoRef = useRef(null)
  const [estado, setEstado] = useState(null)
  const [error, setError] = useState('')
  const [transicion, setTransicion] = useState('corte')
  const [duracion, setDuracion] = useState(0.6)
  const [narrar, setNarrar] = useState(true)
  const [marcaIntro, setMarcaIntro] = useState('')
  const [marcaCierre, setMarcaCierre] = useState('')
  const [musica, setMusica] = useState(null)
  const [midiendo, setMidiendo] = useState(false)

  const load = useCallback(() => {
    api.getPelicula(projectId).then((e) => {
      setEstado(e)
      if (e?.opciones) {
        setTransicion(e.opciones.transicion || 'corte')
        setDuracion(e.opciones.duracion_transicion ?? 0.6)
        setNarrar(e.opciones.narracion !== false)
        setMarcaIntro(e.opciones.intro_job_id || '')
        setMarcaCierre(e.opciones.cierre_job_id || '')
        setMusica(e.opciones.musica || null)
      }
    }).catch(() => setEstado(null))
  }, [projectId])

  useEffect(() => { load() }, [load])

  // Mientras monta se sondea; el resultado durable vive en pelicula.json.
  const montando = estado?.estado === 'montando'
  useEffect(() => {
    if (!montando) return
    const t = setInterval(load, 4000)
    return () => clearInterval(t)
  }, [montando, load])

  // Candidatos a marca: renders vigentes de un proyecto cuyo nombre empieza
  // por "Marca" (el catalogo tiene «Marca intro y cierre»). El nombre del
  // curso no viene en el job: lo resuelve el store compartido del catalogo,
  // igual que la tira de la cola y los avisos de fin de render.
  const catalogo = useCatalogo()
  const marcas = useMemo(() => (jobs || [])
    .filter((j) => j.status === 'done')
    .map((j) => ({ job: j, curso: cursoDeJob(j, catalogo) }))
    .filter(({ curso }) => curso && /^marca/i.test(curso.name)),
  [jobs, catalogo])

  const montar = async () => {
    setError('')
    try {
      await api.montarPelicula(projectId, {
        transicion,
        duracion_transicion: Number(duracion),
        narracion: narrar,
        intro_job_id: marcaIntro || null,
        cierre_job_id: marcaCierre || null,
        musica,
      })
      load()
    } catch (err) { setError(err.message) }
  }

  const cancelar = async () => {
    try { await api.cancelarPelicula(projectId) } catch (err) { setError(err.message) }
    load()
  }

  const verificar = async () => {
    setError('')
    setMidiendo(true)
    try { await api.verificarPelicula(projectId) } catch (err) { setError(err.message) }
    setMidiendo(false)
    load()
  }

  const borrar = async () => {
    try { await api.borrarPelicula(projectId) } catch (err) { setError(err.message) }
    load()
  }

  if (!estado) return null

  const meta = PELI_META[estado.estado] || PELI_META.sin_montar
  const informe = estado.informe
  const hayVideo = Boolean(informe) && estado.estado !== 'sin_montar'
  const puedeMontar = estado.piezas > 0 && !montando
  const recodifica = transicion !== 'corte'
  const runError = estado.run?.estado === 'error' ? estado.run.error : ''

  // Las piezas de la regleta: las MEDIDAS del informe si ya se montó (son la
  // verdad), y si no las previstas con lo que la narración ya midió de cada
  // clip. Antes de montar puede faltar alguna: la regleta se dibuja con las
  // que haya, no se esconde.
  const piezasRegleta = informe?.detalle?.length
    ? informe.detalle.map((d) => ({ ...d, marca: /marca/i.test(d.titulo) }))
    : (clips || [])
      .filter((c) => c.status === 'rendered' || c.status === 'stale')
      .map((c) => ({
        titulo: c.title,
        duracion: duraciones?.[c.id] || 0,
        voz: Boolean(narrarConVoz?.[c.id]),
        cama: c.audio?.has_audio,
        marca: false,
      }))

  return (
    <section className="rounded-lg border border-line bg-surface-2 p-3 space-y-3">
      <header className="flex flex-wrap items-center gap-2">
        <Clapperboard className="h-4 w-4 text-accent" />
        <h3 className="text-sm font-semibold">La película</h3>
        <span className={cn('text-xs', meta.tone)}>{meta.label}</span>
        <span className="text-xs text-muted ml-auto">
          {estado.piezas} pieza{estado.piezas === 1 ? '' : 's'}
          {estado.con_voz > 0 ? ` · ${estado.con_voz} con voz` : ''}
          {estado.faltan?.length > 0 ? ` · ${estado.faltan.length} sin render` : ''}
        </span>
      </header>

      {estado.problema && !hayVideo && (
        <p className="text-xs text-muted">{estado.problema}</p>
      )}

      <div className="flex flex-wrap items-end gap-2">
        <label className="text-xs text-muted space-y-1">
          <span className="block">Empalme entre clips</span>
          <Select value={transicion} onValueChange={setTransicion}>
            <SelectTrigger className="h-8 w-56 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              {(estado.transiciones || ['corte']).map((t) => (
                <SelectItem key={t} value={t}>{TRANSICION_LABEL[t] || t}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </label>

        {recodifica && (
          <label className="text-xs text-muted space-y-1">
            <span className="block">Duración</span>
            <Select value={String(duracion)} onValueChange={(v) => setDuracion(Number(v))}>
              <SelectTrigger className="h-8 w-24 text-xs"><SelectValue /></SelectTrigger>
              <SelectContent>
                {[0.3, 0.5, 0.6, 0.8, 1.0, 1.5].map((d) => (
                  <SelectItem key={d} value={String(d)}>{d.toFixed(1)} s</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </label>
        )}

        {marcas.length > 0 && (
          <>
            <label className="text-xs text-muted space-y-1">
              <span className="block">Intro de marca</span>
              <Select value={marcaIntro || 'ninguno'}
                onValueChange={(v) => setMarcaIntro(v === 'ninguno' ? '' : v)}>
                <SelectTrigger className="h-8 w-44 text-xs"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="ninguno">sin intro</SelectItem>
                  {marcas.map(({ job }) => (
                    <SelectItem key={job.id} value={job.id}>{job.scene}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label className="text-xs text-muted space-y-1">
              <span className="block">Cierre de marca</span>
              <Select value={marcaCierre || 'ninguno'}
                onValueChange={(v) => setMarcaCierre(v === 'ninguno' ? '' : v)}>
                <SelectTrigger className="h-8 w-44 text-xs"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="ninguno">sin cierre</SelectItem>
                  {marcas.map(({ job }) => (
                    <SelectItem key={job.id} value={job.id}>{job.scene}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
          </>
        )}

        <label className="flex items-center gap-1.5 text-xs text-muted">
          <input type="checkbox" checked={narrar}
            onChange={(e) => setNarrar(e.target.checked)}
            className="h-3.5 w-3.5 accent-[var(--accent)]" />
          pegar la narración
        </label>
      </div>

      <div className="space-y-1 border-t border-line pt-2">
        <span className="text-xs text-muted">Cama musical del curso</span>
        <MusicaSelector valor={musica} temas={estado.temas || []}
          dbDefecto={estado.musica_db ?? -24} onChange={setMusica} />
        {musica && (
          <p className="text-[11.5px] text-faint">
            Se sintetiza con la duración medida del montaje y se agacha 9 dB
            donde hay voz. Cambiar de tema o de nivel desactualiza la película.
          </p>
        )}
      </div>

      {recodifica && (
        <p className="text-xs text-warn">
          Un empalme que no es corte <strong>recodifica la película entera</strong>:
          en el servidor (1,5 vCPU) un curso de media hora puede tardar decenas de
          minutos. El corte seco tarda segundos porque copia el vídeo.
        </p>
      )}

      <div className="flex flex-wrap gap-1.5">
        {montando ? (
          <>
            <Button size="sm" variant="default" disabled>
              <Film className="h-3.5 w-3.5 animate-pulse" /> Montando {estado.run?.piezas} piezas…
            </Button>
            <Button size="sm" variant="ghost" onClick={cancelar}>
              <Square className="h-3.5 w-3.5" /> Cancelar
            </Button>
          </>
        ) : (
          <Button size="sm" variant="default" onClick={montar} disabled={!puedeMontar}
            title={puedeMontar ? undefined : 'ningún clip tiene render vigente'}>
            <Play className="h-3.5 w-3.5" />
            {hayVideo ? 'Volver a montar' : 'Montar la película'}
          </Button>
        )}
        {hayVideo && (
          <>
            <Button size="sm" variant="default" asChild>
              <a href={peliculaVideoUrl(projectId)}
                download={`${projectName || 'curso'}.mp4`}>
                <Download className="h-3.5 w-3.5" /> Descargar (.mp4)
              </a>
            </Button>
            <Button size="sm" variant="default" onClick={verificar} disabled={midiendo}>
              <Ruler className="h-3.5 w-3.5" />
              {midiendo ? 'Midiendo…' : 'Medir la película'}
            </Button>
            <Button size="sm" variant="ghost" onClick={borrar} disabled={montando}>
              <Trash2 className="h-3.5 w-3.5" /> Borrar película
            </Button>
          </>
        )}
      </div>

      {(error || runError) && (
        <p className="text-xs text-danger">{error || runError}</p>
      )}

      {piezasRegleta.length > 0 && (
        <Regleta piezas={piezasRegleta} transicion={transicion}
          duracionTransicion={Number(duracion)}
          onIr={(t) => { if (videoRef.current) videoRef.current.currentTime = t }} />
      )}

      {hayVideo && (
        // El curso montado se ve AQUI, no descargándolo: hacer clic en un
        // tramo de la regleta salta a ese punto.
        <video ref={videoRef} controls preload="metadata"
          src={peliculaVideoUrl(projectId)}
          className="max-h-[320px] w-full rounded border border-line bg-black object-contain"
          aria-label={`película de ${projectName || 'el curso'}`} />
      )}

      {informe && (
        <dl className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          <div><dt className="text-muted">Duración</dt>
            <dd className="font-mono">{fmtDur(informe.duracion)}</dd></div>
          <div><dt className="text-muted">Resolución</dt>
            <dd className="font-mono">{informe.resolucion || '—'}</dd></div>
          <div><dt className="text-muted">Tamaño</dt>
            <dd className="font-mono">{fmtMB(informe.bytes)}</dd></div>
          <div><dt className="text-muted">Empalme</dt>
            <dd className="font-mono">{informe.transicion || 'corte'}</dd></div>
        </dl>
      )}

      {hayVideo && (() => {
        const vm = VERIF_META[estado.verificacion] || VERIF_META.sin_verificar
        const v = informe?.verificacion
        return (
          <div className="space-y-1 border-t border-line pt-2">
            <p className="flex flex-wrap items-center gap-2 text-xs">
              <CheckCircle2 className={cn('h-3.5 w-3.5', vm.tone)} />
              <span className="text-muted">La medición:</span>
              <span className={vm.tone}>{vm.label}</span>
              {v && estado.verificacion !== 'sin_verificar' && (
                <span className="font-mono text-[11px] text-faint">
                  dura {v.duracion_medida} s sobre {v.duracion_prevista} previstos
                  ({v.desfase >= 0 ? '+' : ''}{v.desfase} s, tolerancia ±{v.tolerancia})
                  {v.mudas > 0 && ` · ${v.mudas} piezas sin su sonido`}
                </span>
              )}
            </p>
            {v?.problemas?.length > 0 && estado.verificacion === 'no_pasa' && (
              <ul className="rounded border border-err/40 bg-err/10 p-2">
                {v.problemas.map((x, i) => (
                  <li key={i} className="text-[12.5px] text-err">· {x}</li>
                ))}
              </ul>
            )}
          </div>
        )
      })()}

      {estado.estado === 'desactualizada' && (
        <p className="text-xs text-warn">
          Cambió un render, la narración o las opciones desde que se montó:
          esta película ya no corresponde al curso.
        </p>
      )}
    </section>
  )
}
