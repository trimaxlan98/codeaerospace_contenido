// El detalle de un curso: lo que el pipeline necesita mirar de un vistazo
// —estado de render por clip, DURACION del video (el formato pide 28-45 s) y
// estado de narracion— mas las acciones que lo mueven.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Copy, Cpu, Download, FileArchive, FileJson, Layers, Mic, Pencil, Plus, RefreshCw,
  Square, Wand2,
} from 'lucide-react'
import {
  api, projectArchiveUrl, projectExportUrl, projectSourcesUrl, videoUrl,
} from '../../api.js'
import { refreshCatalogo, splitName } from '../../catalogo.js'
import { FONDOS, formatosDe } from '../../formatos.js'
import { usePref } from '../../prefs.js'
import ClipAssistant from '../ClipAssistant.jsx'
import AudioPromoDialog from '../AudioPromoDialog.jsx'
import PeliculaPanel from '../PeliculaPanel.jsx'
import PresentacionPanel from '../PresentacionPanel.jsx'
import GuionDialog from '../GuionDialog.jsx'
import { LoteProgreso, RenderLoteDialog, useLote } from '../RenderLote.jsx'
import VozSelector, { PROVEEDOR_LABEL, vozInicial } from '../VozSelector.jsx'
import { Button } from '../ui/button.jsx'
import { Input } from '../ui/input.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select.jsx'
import AddClipDialog from './AddClipDialog.jsx'
import ClipCard from './ClipCard.jsx'
import DuplicarProyectoDialog from './DuplicarProyectoDialog.jsx'
import HistorialScriptDialog from './HistorialScriptDialog.jsx'
import StyleDialog from './StyleDialog.jsx'
import { Stat } from './insignias.jsx'
import {
  fmtTotal, QUALITY_LABEL, rangoDuracion, resumenAudio, staleWithoutActiveJob,
} from './meta.js'

export default function ProjectDetail({ projectId, jobs, onEditClip, onBack, onOpen, aiEnabled }) {
  const [project, setProject] = useState(null)
  const [narracion, setNarracion] = useState(null)
  const [error, setError] = useState('')
  const [styleOpen, setStyleOpen] = useState(false)
  const [addClipOpen, setAddClipOpen] = useState(false)
  const [loteOpen, setLoteOpen] = useState(false)
  const [duplicarOpen, setDuplicarOpen] = useState(false)
  const [assistantOpen, setAssistantOpen] = useState(false)
  // Modo guiado apagado (el valor por defecto) = esta vista es exactamente la
  // de siempre: ni el boton del asistente se monta.
  const guided = usePref('guided')
  const [guionClip, setGuionClip] = useState(null) // clip cuyo guion se edita/narra
  // Proveedor y voz con que se narra (R1): parte del defecto que anuncia el
  // backend y se recuerda mientras dure la vista.
  const [voz, setVoz] = useState({ proveedor: null, voz: null })
  const [audioClip, setAudioClip] = useState(null) // clip cuyo audio se edita
  const [historialClip, setHistorialClip] = useState(null) // clip cuyo script se compara
  // Resumen del manifiesto de audio por clip (tema de musica, efectos,
  // frases): lo pinta la fila de audio de cada tarjeta. Ver `cargarAudio`.
  const [audioResumen, setAudioResumen] = useState({})
  const [audioNonce, setAudioNonce] = useState(0)
  const savedRef = useRef({ name: '', description: '' })
  const savedClipsRef = useRef({})
  const prevJobsRef = useRef([])

  const load = useCallback(() => {
    setError('')
    api.getProject(projectId).then((p) => {
      setProject(p)
      savedRef.current = { name: p.name, description: p.description }
      savedClipsRef.current = Object.fromEntries(
        p.clips.map((c) => [c.id, { title: c.title, scene: c.scene, final_state: c.final_state, notes: c.notes }]),
      )
    }).catch((err) => setError(err.message))
  }, [projectId])

  useEffect(() => { load() }, [load])

  const loadNarracion = useCallback(() => {
    api.getNarracion(projectId).then((n) => {
      setNarracion(n)
      setVoz((v) => (v.proveedor ? v : vozInicial(n)))
    }).catch(() => setNarracion(null))
  }, [projectId])

  useEffect(() => { loadNarracion() }, [loadNarracion])

  // El manifiesto de audio NO viaja en el detalle: `clip_public` quita
  // `audio_json` a proposito y solo deja `audio = {estado, has_audio}`. Para
  // que la fila de audio pueda decir QUE tema suena y CUANTOS efectos hay,
  // hay que pedirlo clip a clip — asi que se pide solo para los que ya tienen
  // manifiesto (los demas no tienen nada que contar) y una sola vez por
  // carga. En un curso normal eso son cero peticiones; en uno con cama de
  // sonido, una por clip con cama.
  const conManifiesto = useMemo(
    () => (project?.clips || [])
      .filter((c) => c.audio && c.audio.estado !== 'sin_manifiesto')
      .map((c) => c.id),
    [project])
  const claveManifiestos = conManifiesto.join(',')

  useEffect(() => {
    if (!claveManifiestos) { setAudioResumen({}); return }
    let vivo = true
    const ids = claveManifiestos.split(',')
    Promise.all(ids.map((cid) => api.getAudioPromo(projectId, cid)
      .then((d) => [cid, resumenAudio(d.manifiesto)])
      .catch(() => null)))
      .then((pares) => {
        if (vivo) setAudioResumen(Object.fromEntries(pares.filter(Boolean)))
      })
    return () => { vivo = false }
  }, [projectId, claveManifiestos, audioNonce])

  // `run` es GLOBAL (una sola narracion a la vez en toda la app): hay que
  // distinguir la corrida de ESTE proyecto de la de otro. Antes se tomaba
  // cualquier corrida como propia, asi que un proyecto ajeno mostraba
  // "Narrando 3/9…" y su boton Cancelar abortaba el trabajo del otro.
  const run = narracion?.run && !narracion.run.finished ? narracion.run : null
  const narrRun = run && run.project_id === projectId ? run : null
  const runAjena = run && run.project_id !== projectId ? run : null

  // Mientras hay una narracion en curso (propia o ajena, porque libera el
  // unico turno) se sondea el estado cada 3 s; el resultado durable vive en
  // estado.json del backend, esto es solo progreso.
  useEffect(() => {
    if (!run) return
    const t = setInterval(loadNarracion, 3000)
    return () => clearInterval(t)
  }, [run != null, loadNarracion]) // eslint-disable-line react-hooks/exhaustive-deps

  // Refresco cuando un job ligado a un clip de este proyecto pasa a estado
  // terminal (p.ej. termina un render disparado desde aqui): se compara con
  // el estado previo de `jobs`, igual que el patron de App.jsx con jobsRef.
  useEffect(() => {
    const prevJobs = prevJobsRef.current
    prevJobsRef.current = jobs
    const clipIds = new Set((project?.clips || []).map((c) => c.id))
    if (clipIds.size === 0) return
    const becameTerminal = jobs.some((j) => {
      if (!j.clip_id || !clipIds.has(j.clip_id)) return false
      const wasActive = prevJobs.find((p) => p.id === j.id)?.status
      const terminal = j.status !== 'queued' && j.status !== 'running'
      return terminal && (wasActive === 'queued' || wasActive === 'running')
    })
    if (becameTerminal) { load(); loadNarracion() }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- solo reacciona a cambios de `jobs`
  }, [jobs])

  // Progreso agregado del lote de renders. `jobs` (la cola global, por SSE)
  // hace de disparador: cuando un render termina, el lote cambia.
  const { lote, refrescar: refrescarLote } = useLote(projectId, jobs)

  const updateClipLocal = (cid, patch) => {
    setProject((p) => (p ? { ...p, clips: p.clips.map((c) => (c.id === cid ? { ...c, ...patch } : c)) } : p))
  }

  const onFieldChange = (cid, field, value) => updateClipLocal(cid, { [field]: value })

  const onFieldBlur = async (cid, field) => {
    const clip = project?.clips.find((c) => c.id === cid)
    const saved = savedClipsRef.current[cid]
    if (!clip || !saved || clip[field] === saved[field]) return
    try {
      const updated = await api.patchClip(project.id, cid, { [field]: clip[field] })
      if (field === 'scene' || field === 'script') {
        // clip_public no devuelve status/stale recalculados: el hash de
        // contenido incluye la escena, asi que hay que recargar el proyecto
        // completo para que el badge refleje el nuevo estado del backend.
        await load()
      } else {
        savedClipsRef.current[cid] = { ...saved, [field]: updated[field] }
        updateClipLocal(cid, { [field]: updated[field], updated_at: updated.updated_at })
      }
    } catch (err) {
      setError(err.message)
      updateClipLocal(cid, { [field]: saved[field] }) // revertir
    }
  }

  const saveName = async () => {
    if (!project || project.name === savedRef.current.name) return
    if (!project.name.trim()) { setProject((p) => ({ ...p, name: savedRef.current.name })); return }
    try {
      const updated = await api.patchProject(project.id, { name: project.name })
      savedRef.current.name = updated.name
      setProject((p) => ({ ...p, name: updated.name, updated_at: updated.updated_at }))
    } catch (err) {
      setError(err.message)
      setProject((p) => ({ ...p, name: savedRef.current.name }))
    }
  }

  // El formato define el archivo que sale: cambiarlo con videos vigentes
  // dejaria el proyecto con clips de dos tamanos. El backend lo rechaza con
  // 409; aqui el select se deshabilita para que ni se intente.
  const saveFormato = async (valor) => {
    setError('')
    try {
      await api.patchProject(project.id, { formato: valor })
      await load() // `specs` lo recalcula el backend, no el navegador
    } catch (err) {
      setError(err.message)
    }
  }

  // El fondo se bloquea con los renders vigentes por la misma razon que el
  // formato: cambiarlo dejaria un deck con slides de dos colores distintos.
  const saveFondo = async (valor) => {
    setError('')
    try {
      await api.patchProject(project.id, { fondo: valor })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const saveDescription = async () => {
    if (!project || project.description === savedRef.current.description) return
    try {
      const updated = await api.patchProject(project.id, { description: project.description })
      savedRef.current.description = updated.description
      setProject((p) => ({ ...p, description: updated.description, updated_at: updated.updated_at }))
    } catch (err) {
      setError(err.message)
      setProject((p) => ({ ...p, description: savedRef.current.description }))
    }
  }

  // Arrastrar y soltar clips: soltar sobre una tarjeta es moverse a su
  // posicion, con el MISMO endpoint que las flechas.
  //
  // Que se arrastra vive en un REF, no en el estado. El estado de React se
  // aplica en el siguiente render, y `dragstart` y `drop` pueden ocurrir sin
  // que haya habido uno en medio: entonces `soltar` leia `null` y el clip no
  // se movia. El estado se queda solo para lo visual (atenuar la tarjeta que
  // viaja), donde llegar un render tarde no rompe nada.
  const arrastrandoRef = useRef(null)
  const [arrastrando, setArrastrando] = useState(null)
  const arrastre = {
    activo: arrastrando,
    enCurso: () => arrastrandoRef.current,
    iniciar: (cid) => { arrastrandoRef.current = cid; setArrastrando(cid) },
    terminar: () => { arrastrandoRef.current = null; setArrastrando(null) },
    soltar: (position) => {
      const cid = arrastrandoRef.current
      arrastrandoRef.current = null
      setArrastrando(null)
      if (cid) move(cid, position)
    },
  }

  const move = async (cid, position) => {
    setError('')
    try {
      const { clips } = await api.moveClip(project.id, cid, position)
      setProject((p) => ({ ...p, clips }))
      savedClipsRef.current = Object.fromEntries(
        clips.map((c) => [c.id, { title: c.title, scene: c.scene, final_state: c.final_state, notes: c.notes }]),
      )
    } catch (err) {
      setError(err.message)
    }
  }

  const removeClip = async (cid) => {
    setError('')
    try {
      await api.deleteClip(project.id, cid)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const renderClip = async (cid) => {
    setError('')
    try {
      await api.renderClip(project.id, cid)
    } catch (err) {
      setError(err.message)
    }
  }

  // «Re-renderizar desactualizados» es ahora un lote sin preguntar nada: el
  // endpoint salta solo los clips al dia y los que ya tienen un render en
  // vuelo, asi que el bucle de renders individuales que habia aqui (para no
  // encolar dos veces el mismo clip) sobra.
  const renderAllStale = async () => {
    setError('')
    if (staleWithoutActiveJob(project.clips, jobs).length === 0) return
    try {
      recibirLote(await api.renderLote(project.id, { clips: null, force: false }))
    } catch (err) {
      setError(err.message)
    }
  }

  const recibirLote = (res) => {
    const reales = (res.saltados || []).filter((s) => s.error !== 'al dia'
      && s.error !== 'ya hay un render en curso')
    if (reales.length) {
      setError(`Algunos clips no se pudieron encolar: ${reales.map((s) => s.error).join('; ')}`)
    }
    if (res.calidad_cambiada) load()
    refrescarLote()
  }

  const duplicarClip = async (cid) => {
    setError('')
    try {
      await api.duplicarClip(project.id, cid)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const generarNarracion = async (body = {}) => {
    setError('')
    try {
      await api.startNarracion(project.id, {
        proveedor: voz.proveedor || undefined, voz: voz.voz || undefined, ...body,
      })
      loadNarracion()
    } catch (err) {
      setError(err.message)
    }
  }

  const cancelarNarracion = async () => {
    setError('')
    try {
      await api.cancelNarracion(project.id)
      loadNarracion()
    } catch (err) {
      setError(err.message)
    }
  }

  const openInStudio = async (clip) => {
    setError('')
    try {
      const { script, style_offset } = await api.getClipScript(project.id, clip.id)
      onEditClip({
        projectId: project.id,
        projectName: project.name,
        clipId: clip.id,
        clipTitle: clip.title,
        quality: project.quality,
        styleOffset: style_offset,
      }, script, clip.scene)
    } catch (err) {
      setError(err.message)
    }
  }

  if (!project) {
    return (
      <main data-view="projects" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
        <section className="panel shrink-0 p-4">
          <Button size="xs" variant="ghost" onClick={onBack}>← Proyectos</Button>
          <p className="mt-2 text-[13px] text-muted">
            {error ? <span role="alert" className="text-warn">{error}</span> : 'Cargando proyecto…'}
          </p>
        </section>
      </main>
    )
  }

  const clips = [...project.clips].sort((a, b) => a.position - b.position)
  const renderedCount = clips.filter((c) => c.status === 'rendered').length
  // Cuenta solo los stale/no_render sin job en vuelo: coherente con lo que
  // "Re-renderizar desactualizados" realmente va a encolar.
  const staleCount = staleWithoutActiveJob(clips, jobs).length
  const formatoFijo = clips.some((c) => c.job_id)
  const esPromo = (project.tipo || 'curso') === 'promo'
  const esPresentacion = (project.tipo || 'curso') === 'presentacion'
  // Una pieza cuyo fondo es una simulacion (paquete `emergencia`) no cuesta
  // lo que un clip normal: la pila de fotogramas se calcula en el render y
  // luego cada frame se compone a 1080x1920. Medido: ~0.29 s/frame en qh, o
  // sea HORAS por pieza en este VPS (1.5 vCPU). Se detecta por el codigo —no
  // por la plantilla— porque el clip se puede escribir a mano.
  const usaSimulacion = /(^|\n)\s*(import\s+emergencia|from\s+emergencia[\s.])|emergencia\.\w|em\.(Pelicula|bandada|moho|arena|vida|turing|ondas|chladni|ising|pendulos|cuencas|epiciclos|rio|galaxias)\b/
    .test([project.style_block || '', ...clips.map((c) => c.script || '')].join('\n'))
  const audioAlDia = clips.filter((c) => c.audio?.estado === 'al_dia').length
  // El promo se descarga como lo que es: un mp4 (el que sirve la app, ya
  // mezclado si se mezclo), no como un zip de curso con concat.txt.
  const videoPromo = esPromo && clips[0]?.status === 'rendered' ? clips[0].job_id : null
  const narrByClip = Object.fromEntries((narracion?.clips || []).map((c) => [c.clip_id, c]))
  const narrPending = (narracion?.clips || []).filter((c) => c.estado !== 'al_dia').length
  const narrAlDia = (narracion?.clips || []).filter((c) => c.estado === 'al_dia').length
  const narrErrores = (narracion?.run?.finished && narracion.run.errores) || []

  // Duraciones: el pipeline pide 28-45 s por clip. Se leen del estado de
  // narracion, que ya calcula `video_s` del mp4 vigente de cada clip.
  const duraciones = clips.map((c) => narrByClip[c.id]?.video_s).filter((s) => s != null)
  const totalDur = duraciones.reduce((a, s) => a + s, 0)
  const rango = rangoDuracion(project.tipo)
  const fueraRango = duraciones.filter((s) => s < rango.min || s > rango.max).length
  const { family, label } = splitName(project.name)

  return (
    <main data-view="projects" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <section className="panel shrink-0" aria-label="cabecera del proyecto">
        <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
          <Button size="xs" variant="ghost" onClick={onBack}>← Proyectos</Button>
          {family && <span className="truncate font-mono text-[11px] text-accent">{family}</span>}
          <span className="font-mono text-[11px] text-faint">
            {clips.length} clip{clips.length === 1 ? '' : 's'}
          </span>
        </div>

        <div className="flex flex-col gap-3 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex min-w-0 flex-1 flex-col gap-1.5">
              <Input value={project.name} onChange={(e) => setProject((p) => ({ ...p, name: e.target.value }))}
                onBlur={saveName} aria-label="nombre del proyecto"
                className="h-auto max-w-md border-transparent bg-transparent px-0 font-display text-lg font-semibold text-ink hover:border-line focus-visible:border-line focus-visible:bg-canvas focus-visible:px-2" />
              <Input value={project.description || ''}
                onChange={(e) => setProject((p) => ({ ...p, description: e.target.value }))}
                onBlur={saveDescription} placeholder="Descripción (opcional)" aria-label="descripción del proyecto"
                className="h-auto max-w-lg border-transparent bg-transparent px-0 text-[13px] text-muted hover:border-line focus-visible:border-line focus-visible:bg-canvas focus-visible:px-2" />
            </div>
            <div className="flex shrink-0 items-center gap-1.5">
              <span className="rounded-md border border-accent/40 px-2.5 py-1 font-mono text-[11px] uppercase tracking-wide text-accent"
                title={project.specs ? `${project.specs.resolution} a ${project.specs.fps} fps` : undefined}>
                {QUALITY_LABEL[project.quality] || project.quality}
                {project.specs && (
                  <span className="text-accent/70"> · {project.specs.resolution.replace('x', '×')}</span>
                )}
              </span>
              <Select value={project.formato || 'horizontal'} onValueChange={saveFormato}
                disabled={formatoFijo}>
                <SelectTrigger className="h-[26px] w-[172px] text-[12px]"
                  title={formatoFijo
                    ? 'hay clips con render vigente: el formato queda fijo hasta borrar esos videos'
                    : 'el mismo código sale en 9:16 o en 16:9; lo aplica la escena al renderizar'}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {formatosDe(project.tipo || 'curso').map((f) => (
                    <SelectItem key={f.id} value={f.id}>{f.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {esPresentacion && (
                <Select value={project.fondo || 'marca'} onValueChange={saveFondo}
                  disabled={formatoFijo}>
                  <SelectTrigger className="h-[26px] w-[196px] text-[12px]"
                    title={formatoFijo
                      ? 'hay clips con render vigente: el fondo queda fijo hasta borrar esos vídeos'
                      : 'el color del slide; la paleta de textos se voltea sola para que se lea sobre él'}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {FONDOS.map((f) => (
                      <SelectItem key={f.id} value={f.id}>{f.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
          </div>

          {usaSimulacion && (
            <p className="flex items-start gap-2 rounded-lg border border-warn/40 bg-warn/10 px-3 py-2 text-[12px] leading-snug text-warn">
              <Cpu className="mt-px size-3.5 shrink-0" aria-hidden="true" />
              <span>
                <strong className="font-semibold">El render final de esta pieza se hace en local.</strong>{' '}
                El fotograma entero es una simulación (paquete <code>emergencia</code>): en este
                servidor va a ~0.29 s por frame, así que una pieza de 35 s en <code>qh</code> son
                horas. Aquí conviene previsualizar en <code>ql</code>; el render bueno, con{' '}
                <code>studio/tools/render_vertical.py</code> en tu máquina. Guía:{' '}
                <code>studio/docs/EMERGENCIA.md</code>.
              </span>
            </p>
          )}

          {/* Panel de estado del curso: lo que hay que mirar antes de exportar. */}
          <div className="grid grid-cols-[repeat(auto-fit,minmax(120px,1fr))] gap-2">
            <Stat label="Render" value={`${renderedCount}/${clips.length}`}
              tone={renderedCount === clips.length && clips.length > 0 ? 'ok' : 'warn'}
              detail={staleCount > 0 ? `${staleCount} por rehacer` : 'todo vigente'} />
            <Stat label="Duración" value={fmtTotal(totalDur)}
              tone={fueraRango > 0 ? 'warn' : 'ok'}
              detail={duraciones.length < clips.length
                ? `${duraciones.length}/${clips.length} medidos`
                : fueraRango > 0 ? `${fueraRango} fuera de ${rango.min}-${rango.max} s` : `${rango.min}-${rango.max} s por clip`} />
            {/* Un promo no se narra por el camino de los cursos (guion escrito
                por Gemini a 28-45 s): su voz y su cama viven en el manifiesto
                de audio del clip. Aqui se cuenta eso. */}
            {esPromo ? (
              <Stat label="Audio" value={`${audioAlDia}/${clips.length}`}
                tone={audioAlDia === clips.length && clips.length > 0 ? 'ok' : 'muted'}
                detail={audioAlDia === clips.length && clips.length > 0
                  ? 'mezclado' : 'sin mezclar'} />
            ) : (
              <Stat label="Narración" value={narracion ? `${narrAlDia}/${clips.length}` : '—'}
                tone={narracion && narrAlDia === clips.length && clips.length > 0 ? 'ok' : 'muted'}
                detail={narracion?.enabled === false ? 'sin proveedor de voz'
                  : voz.proveedor ? `${PROVEEDOR_LABEL[voz.proveedor] || voz.proveedor} · ${voz.voz || ''}` : '…'} />
            )}
          </div>

          <div className="flex flex-wrap gap-1.5">
            <Button size="sm" variant="default" asChild>
              <a href={projectExportUrl(project.id)} target="_blank" rel="noreferrer">
                <FileJson className="h-3.5 w-3.5" /> Exportar manifest
              </a>
            </Button>
            {esPromo ? (
              videoPromo ? (
                <Button size="sm" variant="default" asChild>
                  <a href={videoUrl(videoPromo)} download={`${project.name || 'promo'}.mp4`}>
                    <Download className="h-3.5 w-3.5" /> Descargar promo (.mp4)
                  </a>
                </Button>
              ) : (
                <Button size="sm" variant="default" disabled title="Todavía no hay render vigente">
                  <Download className="h-3.5 w-3.5" /> Descargar promo (.mp4)
                </Button>
              )
            ) : renderedCount > 0 ? (
              <Button size="sm" variant="default" asChild>
                <a href={projectArchiveUrl(project.id)} download={`${project.name || 'curso'}.zip`}>
                  <Download className="h-3.5 w-3.5" /> Descargar curso (.zip)
                </a>
              </Button>
            ) : (
              <Button size="sm" variant="default" disabled title="Ningún clip renderizado todavía">
                <Download className="h-3.5 w-3.5" /> Descargar curso (.zip)
              </Button>
            )}
            <Button size="sm" variant="default" asChild>
              <a href={projectSourcesUrl(project.id)}
                download={`${project.name || 'curso'}-fuentes.zip`}
                title="curso.json + style_block.py + un .py por clip (+ guiones): lo que vuelve a leer subir_curso.py">
                <FileArchive className="h-3.5 w-3.5" /> Fuentes (.zip)
              </a>
            </Button>
            <Button size="sm" variant="default" onClick={renderAllStale} disabled={staleCount === 0}
              title={staleCount === 0 ? 'no hay clips desactualizados sin un render en curso' : undefined}>
              <RefreshCw className="h-3.5 w-3.5" /> Re-renderizar desactualizados{staleCount > 0 ? ` (${staleCount})` : ''}
            </Button>
            <Button size="sm" variant="default" onClick={() => setLoteOpen(true)}
              disabled={clips.length === 0}
              title="encola varios clips en orden, a la calidad que elijas">
              <Layers className="h-3.5 w-3.5" /> Render en lote…
            </Button>
            {esPromo || !narracion?.proveedores ? null : (
              <VozSelector proveedores={narracion.proveedores} value={voz} onChange={setVoz}
                disabled={Boolean(narrRun)} compact />
            )}
            {esPromo ? null : narrRun ? (
              <>
                <Button size="sm" variant="default" disabled>
                  <Mic className="h-3.5 w-3.5 animate-pulse" /> Narrando {Math.min(narrRun.done + 1, narrRun.total)}/{narrRun.total}…
                </Button>
                <Button size="sm" variant="ghost" onClick={cancelarNarracion}>
                  <Square className="h-3.5 w-3.5" /> Cancelar narración
                </Button>
              </>
            ) : (
              <Button size="sm" variant="default" onClick={() => generarNarracion()}
                disabled={!narracion?.enabled || narrPending === 0 || Boolean(runAjena)}
                title={!narracion?.enabled
                  ? 'ningún proveedor de voz disponible (edge-tts, Piper o Vertex)'
                  : runAjena
                    ? 'hay una narración en curso en otro proyecto (solo una a la vez)'
                    : (narrPending === 0 ? 'la narración de todos los clips está al día' : undefined)}>
                <Mic className="h-3.5 w-3.5" /> Generar narración{narrPending > 0 ? ` (${narrPending})` : ''}
              </Button>
            )}
            <Button size="sm" variant="default" onClick={() => setStyleOpen(true)}>
              <Pencil className="h-3.5 w-3.5" /> Editar estilo
            </Button>
            <Button size="sm" variant="default" onClick={() => setDuplicarOpen(true)}>
              <Copy className="h-3.5 w-3.5" /> Duplicar proyecto
            </Button>
          </div>

          {/* La barra del lote se pinta mientras corre y, si termino con
              fallos, hasta que se lance otro: un lote limpio y terminado no
              dice nada que no diga ya el contador «Render N/N». */}
          {lote && (lote.activo || lote.fallidos > 0) && <LoteProgreso lote={lote} />}
        </div>

        {runAjena && (
          <p role="status" className="border-t border-line bg-cyan/10 px-3 py-1.5 text-[12.5px] text-cyan">
            Hay una narración en curso en otro proyecto ({runAjena.done}/{runAjena.total}).
            Solo se genera una a la vez; este proyecto tendrá que esperar su turno.
          </p>
        )}
        {narrErrores.length > 0 && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">
            Narración con errores: {narrErrores.map((e) => e.error).join('; ')}
          </p>
        )}
        {error && (
          <p role="alert" className="border-t border-line bg-warn/10 px-3 py-1.5 text-[13px] text-warn">{error}</p>
        )}
      </section>

      {/* Cada tipo entrega una cosa distinta: un curso entrega su pelicula,
          una presentación entrega el .pptx que el ponente abre en la sala, y un promo
          es UN clip en bucle que no monta nada. */}
      {esPresentacion ? (
        <PresentacionPanel projectId={project.id} />
      ) : !esPromo && (
        <PeliculaPanel projectId={project.id} projectName={project.name} jobs={jobs}
          clips={clips}
          duraciones={Object.fromEntries(clips.map((c) => [c.id, narrByClip[c.id]?.video_s]))}
          narrarConVoz={Object.fromEntries(clips.map((c) => [c.id, narrByClip[c.id]?.has_audio]))} />
      )}

      <section className="panel flex min-h-0 flex-1 flex-col overflow-hidden" aria-label="clips del proyecto">
        <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
          <span className="eyebrow">Clips · {label}</span>
          <div className="flex items-center gap-1.5">
            {guided && (
              <Button size="xs" variant="accent" onClick={() => setAssistantOpen(true)}
                title="Escribe el script del clip a partir de un formulario">
                <Wand2 className="h-3.5 w-3.5" /> Asistente
              </Button>
            )}
            <Button size="xs" variant="primary" onClick={() => setAddClipOpen(true)}>
              <Plus className="h-3.5 w-3.5" /> Añadir clip
            </Button>
          </div>
        </div>
        <div className="min-h-0 flex-1 overflow-auto">
          {clips.length === 0 ? (
            <p className="p-4 text-[13px] text-muted">Sin clips todavía. Añade el primero para empezar el curso.</p>
          ) : (
            clips.map((clip, i) => (
              <ClipCard key={clip.id} clip={clip} index={i} total={clips.length}
                prevClip={i > 0 ? clips[i - 1] : null} jobs={jobs}
                onFieldChange={onFieldChange} onFieldBlur={onFieldBlur}
                onMove={move} onDelete={removeClip} onRender={renderClip} arrastre={arrastre}
                onDuplicate={duplicarClip}
                onOpenInStudio={openInStudio}
                onHistorial={setHistorialClip}
                projectId={project.id} formato={project.formato} tipo={project.tipo}
                narr={narrByClip[clip.id]}
                narrando={narrRun?.current?.clip_id === clip.id}
                narrBusy={Boolean(run)} narrEnabled={Boolean(narracion?.enabled)}
                audioResumen={audioResumen[clip.id]}
                onVerGuion={() => setGuionClip(clip)}
                onAudio={() => setAudioClip(clip)}
                onNarrar={() => generarNarracion({ clips: [clip.id], force: true })} />
            ))
          )}
        </div>
      </section>

      <RenderLoteDialog open={loteOpen} onOpenChange={setLoteOpen} project={project}
        staleCount={staleCount} onLanzado={recibirLote} />
      <DuplicarProyectoDialog open={duplicarOpen} onOpenChange={setDuplicarOpen}
        project={project} onDuplicado={(p) => { setDuplicarOpen(false); refreshCatalogo(); onOpen(p.id) }} />
      <StyleDialog open={styleOpen} onOpenChange={setStyleOpen} project={project}
        onSaved={(styleBlock, updatedAt) => setProject((p) => ({ ...p, style_block: styleBlock, updated_at: updatedAt }))} />
      <AddClipDialog open={addClipOpen} onOpenChange={setAddClipOpen} projectId={project.id}
        onCreated={() => { setAddClipOpen(false); load() }} />
      {audioClip && (
        <AudioPromoDialog projectId={project.id} clip={audioClip}
          onOpenChange={(o) => !o && setAudioClip(null)}
          onSaved={() => { load(); setAudioNonce((n) => n + 1) }} />
      )}
      {/* Guardar el manifiesto puede cambiar el tema de música sin mover el
          estado de la mezcla, así que el resumen de los chips se refresca por
          su propio contador y no por el estado del clip. */}

      <HistorialScriptDialog projectId={project.id} clip={historialClip}
        job={historialClip ? jobs.find((j) => j.id === historialClip.job_id) : null}
        onOpenChange={(o) => !o && setHistorialClip(null)}
        onRestaurado={() => { setHistorialClip(null); load() }} />

      <GuionDialog projectId={project.id} clip={guionClip} narr={guionClip ? narrByClip[guionClip.id] : null}
        narracion={narracion} voz={voz} onVoz={setVoz}
        onOpenChange={(o) => !o && setGuionClip(null)} onChanged={loadNarracion} />
      {guided && (
        <ClipAssistant open={assistantOpen} onOpenChange={setAssistantOpen}
          project={project} aiEnabled={aiEnabled}
          onCreated={() => { setAssistantOpen(false); load() }} />
      )}
    </main>
  )
}
