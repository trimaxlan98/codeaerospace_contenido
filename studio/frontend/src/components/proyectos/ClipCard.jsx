// Un clip dentro del detalle del curso: miniatura, estado del render,
// continuidad, acciones y la fila de audio.

import { useRef } from 'react'
import { ChevronDown, ChevronUp, Copy, Film, GripVertical, History, Pencil } from 'lucide-react'
import { thumbUrl } from '../../api.js'
import { ratioDeJob } from '../../formatos.js'
import { AUDIO_META, VERIF_META } from '../AudioPromoDialog.jsx'
import { Button } from '../ui/button.jsx'
import { Input } from '../ui/input.jsx'
import DeleteButton from '../DeleteButton.jsx'
import FilaAudio from './FilaAudio.jsx'
import { DurationBadge } from './insignias.jsx'
import { activeJobFor, rangoDuracion, STATUS_META, textareaCls } from './meta.js'
import { cn } from '@/lib/utils'

export default function ClipCard({
  clip, index, total, prevClip, jobs, onFieldChange, onFieldBlur, onMove, onDelete,
  onRender, onDuplicate, onOpenInStudio, onHistorial, projectId, formato, tipo,
  narr, narrando, narrBusy, narrEnabled, onNarrar, onVerGuion, onAudio, audioResumen, arrastre,
}) {
  // Reordenar arrastrando. Quien es `draggable` es EL ASA, no la tarjeta:
  // dentro de la tarjeta hay inputs y un textarea, y un contenedor arrastrable
  // se pelea con la seleccion de texto. La tarjeta solo hace de destino. Para
  // que lo que se arrastra se vea (el asa sola es un icono de 14 px), se le
  // pasa la tarjeta como imagen de arrastre.
  const tarjetaRef = useRef(null)
  const activeJob = activeJobFor(jobs, clip.id)
  // El promo dice en el propio boton como esta su mezcla: sin audio, sin
  // mezclar, desactualizada o al dia.
  // Desde el sprint E3 la cama de sonido tambien es de los cursos (sin voz:
  // esa sale de «Generar narracion»). El estado se enseña igual en los dos.
  const audioMeta = AUDIO_META[clip.audio?.estado] || null
  // El distintivo de verificacion dice lo MEDIDO: si el informe esta al dia,
  // pasa o no pasa; si no, en que estado esta la medicion.
  const verif = tipo === 'promo' ? clip.verificacion : null
  const verifMeta = !verif || verif.estado === 'sin_render' ? null
    : verif.estado === 'al_dia'
      ? (verif.ok ? { label: 'verificado', text: 'text-ok' }
                  : { label: 'no pasa', text: 'text-err' })
      : VERIF_META[verif.estado]
  const renderJob = clip.job_id ? jobs.find((j) => j.id === clip.job_id) : null
  const meta = activeJob ? STATUS_META[activeJob.status] : (STATUS_META[clip.status] || STATUS_META.no_render)
  const canRender = !activeJob && Boolean(clip.scene?.trim())
  // Historial: solo con el clip DESACTUALIZADO y con un render vigente al que
  // volver. Al dia, las dos versiones son la misma por definicion.
  const puedeRestaurar = clip.status === 'stale' && Boolean(clip.job_id)

  return (
    <article
      ref={tarjetaRef}
      onDragOver={(e) => {
        // Se acepta cualquier arrastre propio en curso; el ref es la verdad.
        if (arrastre?.enCurso() && arrastre.enCurso() !== clip.id) {
          e.preventDefault()
          e.dataTransfer.dropEffect = 'move'
        }
      }}
      onDrop={(e) => { e.preventDefault(); arrastre?.soltar(clip.position) }}
      className={cn(
        'flex flex-col gap-2.5 border-b border-line p-3.5 last:border-b-0 sm:flex-row',
        arrastre?.activo === clip.id && 'opacity-40',
        arrastre?.activo && arrastre.activo !== clip.id && 'hover:border-accent')}>
      {/* La proporción sale del video real (o del formato del proyecto
          mientras no exista): un promo vertical no se mira en una caja 16:9. */}
      <div style={{ aspectRatio: ratioDeJob(renderJob, formato) }}
        className="relative max-h-[210px] w-full shrink-0 overflow-hidden rounded-md border border-line bg-canvas sm:w-40">
        {renderJob?.has_thumb ? (
          <img src={thumbUrl(renderJob.id)} alt={`miniatura de ${clip.title}`} loading="lazy"
            className="h-full w-full object-contain" />
        ) : (
          <span className="grid h-full place-items-center text-faint"><Film className="h-6 w-6" /></span>
        )}
      </div>

      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-[11px] text-faint">#{index + 1}</span>
          <Input value={clip.title}
            onChange={(e) => onFieldChange(clip.id, 'title', e.target.value)}
            onBlur={() => onFieldBlur(clip.id, 'title')}
            aria-label="título del clip"
            className="h-7 max-w-xs px-2 text-[13px] font-semibold" />
          <span className={cn('flex items-center gap-1.5 rounded-md border border-line px-2 py-0.5 font-mono text-[11px] uppercase tracking-wide', meta.text)}>
            <span className={cn('h-1.5 w-1.5 rounded-full', meta.dot)} /> {meta.label}
          </span>
          <DurationBadge s={narr?.video_s} rango={rangoDuracion(tipo)} />
          {verifMeta && (
            <span className={cn('rounded-md border border-line px-2 py-0.5 font-mono text-[11px] uppercase tracking-wide', verifMeta.text)}
              title="bucle, duración y audio, medidos sobre el archivo que sirve la app">
              {verifMeta.label}
            </span>
          )}
        </div>

        <label className="flex items-center gap-2 text-[12px] text-muted">
          escena
          <Input value={clip.scene || ''}
            onChange={(e) => onFieldChange(clip.id, 'scene', e.target.value)}
            onBlur={() => onFieldBlur(clip.id, 'scene')}
            placeholder="NombreDeEscena"
            className="h-7 max-w-[220px] px-2 font-mono text-[12px]" />
        </label>

        <details className="rounded-md border border-line/60 bg-canvas/40">
          <summary className="cursor-pointer select-none px-2.5 py-1.5 text-[11.5px] text-muted">
            Continuidad
          </summary>
          <div className="flex flex-col gap-2 border-t border-line/60 px-2.5 py-2 text-[12.5px]">
            <p className="text-muted">
              El clip anterior termina: {prevClip ? (prevClip.final_state?.trim() || 'sin nota') : '— (primer clip)'}
            </p>
            <label className="flex flex-col gap-1">
              <span className="eyebrow">Este clip termina en…</span>
              <textarea value={clip.final_state || ''} rows={2}
                onChange={(e) => onFieldChange(clip.id, 'final_state', e.target.value)}
                onBlur={() => onFieldBlur(clip.id, 'final_state')}
                className={textareaCls} />
            </label>
            <label className="flex flex-col gap-1">
              <span className="eyebrow">Notas</span>
              <textarea value={clip.notes || ''} rows={2}
                onChange={(e) => onFieldChange(clip.id, 'notes', e.target.value)}
                onBlur={() => onFieldBlur(clip.id, 'notes')}
                className={textareaCls} />
            </label>
          </div>
        </details>

        <div className="mt-1 flex flex-wrap items-center gap-1.5">
          <Button size="xs" variant="default" onClick={() => onOpenInStudio(clip)}>
            <Pencil className="h-3.5 w-3.5" /> Editar en Estudio
          </Button>
          <Button size="xs" variant="accent" onClick={() => onRender(clip.id)} disabled={!canRender}
            title={activeJob ? 'ya hay un render en curso para este clip' : (!clip.scene?.trim() ? 'asigna una escena primero' : undefined)}>
            Render
          </Button>
          <span
            draggable
            onDragStart={(e) => {
              e.dataTransfer.effectAllowed = 'move'
              // Firefox no inicia el arrastre si no hay datos.
              e.dataTransfer.setData('text/plain', clip.id)
              if (tarjetaRef.current) {
                e.dataTransfer.setDragImage(tarjetaRef.current, 24, 24)
              }
              arrastre?.iniciar(clip.id)
            }}
            onDragEnd={() => arrastre?.terminar()}
            title="arrastrar para reordenar"
            className="cursor-grab select-none px-1 text-faint hover:text-muted active:cursor-grabbing">
            <GripVertical className="h-3.5 w-3.5" />
          </span>
          <Button size="xs" variant="ghost" onClick={() => onMove(clip.id, clip.position - 1)}
            disabled={index === 0} aria-label="mover arriba">
            <ChevronUp className="h-3.5 w-3.5" />
          </Button>
          <Button size="xs" variant="ghost" onClick={() => onMove(clip.id, clip.position + 1)}
            disabled={index === total - 1} aria-label="mover abajo">
            <ChevronDown className="h-3.5 w-3.5" />
          </Button>
          {/* El único historial que hay: el script del último render que
              funcionó. Solo aparece cuando sirve de algo (clip desactualizado
              con vídeo vigente). */}
          {puedeRestaurar && (
            <Button size="xs" variant="ghost" onClick={() => onHistorial(clip)}
              title="compara el script de ahora con el del último render que funcionó, y permite volver a él">
              <History className="h-3.5 w-3.5" /> Último render
            </Button>
          )}
          <Button size="xs" variant="ghost" onClick={() => onDuplicate(clip.id)}
            title="copia este clip justo detrás (script, escena, notas y audio; sin el render)">
            <Copy className="h-3.5 w-3.5" /> Duplicar
          </Button>
          <span className="ml-auto"><DeleteButton onDelete={() => onDelete(clip.id)} /></span>
        </div>

        {/* Voz, música y SFX en una sola fila, siempre: las tres son
            dimensiones del clip, no cosas que aparecen si el backend ya sabe
            algo de ellas. */}
        <FilaAudio projectId={projectId} clip={clip} tipo={tipo}
          narr={narr} narrando={narrando} narrBusy={narrBusy} narrEnabled={narrEnabled}
          audioMeta={audioMeta} resumen={audioResumen}
          onVoz={tipo === 'promo' ? onAudio : onVerGuion}
          onMezcla={onAudio} onNarrar={onNarrar} />
      </div>
    </article>
  )
}
