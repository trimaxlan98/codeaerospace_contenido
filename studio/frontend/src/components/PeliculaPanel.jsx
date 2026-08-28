// La pelicula del curso: los clips en orden, su narracion y la marca, en un
// solo archivo, montado por la app.
//
// Hasta el sprint E1 esto se hacia fuera: descargar el zip, `unzip`, `sh
// mux.sh`. El panel es deliberadamente pequeno — dos desplegables y un boton —
// porque la decision real es una sola: **corte o transicion**. El corte no
// recodifica (segundos); cualquier otra cosa recodifica la pelicula entera y
// eso hay que decirlo ANTES, no despues de media hora de espera.

import { useCallback, useEffect, useMemo, useState } from 'react'
import { Clapperboard, Download, Film, Play, Square, Trash2 } from 'lucide-react'
import { api, peliculaVideoUrl } from '../api.js'
import { cursoDeJob, useCatalogo } from '../catalogo.js'
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
  const r = Math.round(s % 60)
  return m > 0 ? `${m} min ${String(r).padStart(2, '0')} s` : `${r} s`
}

function fmtMB(bytes) {
  if (!bytes) return '—'
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export default function PeliculaPanel({ projectId, projectName, jobs }) {
  const [estado, setEstado] = useState(null)
  const [error, setError] = useState('')
  const [transicion, setTransicion] = useState('corte')
  const [duracion, setDuracion] = useState(0.6)
  const [narrar, setNarrar] = useState(true)
  const [marcaIntro, setMarcaIntro] = useState('')
  const [marcaCierre, setMarcaCierre] = useState('')

  const load = useCallback(() => {
    api.getPelicula(projectId).then((e) => {
      setEstado(e)
      if (e?.opciones) {
        setTransicion(e.opciones.transicion || 'corte')
        setDuracion(e.opciones.duracion_transicion ?? 0.6)
        setNarrar(e.opciones.narracion !== false)
        setMarcaIntro(e.opciones.intro_job_id || '')
        setMarcaCierre(e.opciones.cierre_job_id || '')
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
      })
      load()
    } catch (err) { setError(err.message) }
  }

  const cancelar = async () => {
    try { await api.cancelarPelicula(projectId) } catch (err) { setError(err.message) }
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
            <Button size="sm" variant="ghost" onClick={borrar} disabled={montando}>
              <Trash2 className="h-3.5 w-3.5" /> Borrar película
            </Button>
          </>
        )}
      </div>

      {(error || runError) && (
        <p className="text-xs text-danger">{error || runError}</p>
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

      {estado.estado === 'desactualizada' && (
        <p className="text-xs text-warn">
          Cambió un render, la narración o las opciones desde que se montó:
          esta película ya no corresponde al curso.
        </p>
      )}
    </section>
  )
}
