// El audio de un clip, en UNA fila (R5a).
//
// Hasta aquí el sonido de un clip de curso estaba repartido en dos sitios que
// no se miraban: un botón «Audio» en la fila de acciones (la cama de SFX y la
// música, `AudioPromoDialog`) y, más abajo y solo si el backend ya sabía algo
// del clip, una fila de narración con «Guion y voz» (`GuionDialog`). Eran las
// tres dimensiones de una misma pregunta —¿cómo suena este clip?— contestadas
// en dos idiomas y a dos alturas.
//
// Ahora es una fila con tres chips de estado: **voz · música · SFX**. Cada uno
// dice lo que hay (no solo que existe la opción) y abre el diálogo que lo
// edita. Lo demás de la fila —el reproductor de la narración, su duración, el
// aviso de «más larga que el vídeo» y el botón de renarrar— se queda como
// estaba: es lo que se mira mientras se ajusta, no una decisión.
//
// Un PROMO juega otro juego: su voz no sale de «Generar narración» (guion de
// 28-45 s escrito por el proveedor) sino de las frases del propio manifiesto,
// así que allí el chip de voz abre el mismo diálogo que los otros dos.

import { AudioLines, Mic, Music2, RefreshCw } from 'lucide-react'
import { narracionAudioUrl } from '../../api.js'
import { Button } from '../ui/button.jsx'
import { NARR_META } from './meta.js'
import { cn } from '@/lib/utils'

// Estados de la mezcla que dicen algo que no diga ya otro distintivo.
const MEZCLA_VISIBLE = new Set(['sin_mezclar', 'desactualizado', 'al_dia'])

function Chip({ icon: Icon, nombre, valor, tone, onClick, title }) {
  return (
    <button type="button" onClick={onClick} title={title}
      className="inline-flex items-center gap-1.5 rounded-md border border-line bg-surface-2 px-2 py-1 text-[11px] transition-colors hover:border-line-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
      <Icon className="h-3 w-3 shrink-0 text-accent" aria-hidden="true" />
      <span className="text-muted">{nombre}</span>
      <span className={cn('font-mono uppercase tracking-wide', tone || 'text-muted')}>{valor}</span>
    </button>
  )
}

export default function FilaAudio({
  projectId, clip, tipo, narr, narrando, narrBusy, narrEnabled,
  audioMeta, resumen, onVoz, onMezcla, onNarrar,
}) {
  const esPromo = tipo === 'promo'
  // `sin_manifiesto` = nadie ha escrito nada de audio en este clip todavía;
  // el resto de estados implican que hay manifiesto que leer.
  const conManifiesto = Boolean(clip.audio && clip.audio.estado !== 'sin_manifiesto')
  // Mientras el manifiesto viaja, «ninguna» sería mentira: se dice «…».
  const cargando = conManifiesto && !resumen

  const narrMeta = narr ? (NARR_META[narr.estado] || NARR_META.sin_narracion) : NARR_META.sin_narracion
  const frases = resumen?.frases || 0
  const voz = esPromo
    ? {
      valor: cargando ? '…' : (frases ? `${frases} frase${frases === 1 ? '' : 's'}` : 'sin voz'),
      tone: frases ? 'text-ok' : 'text-muted',
      title: 'las frases de este promo y su voz, dentro del manifiesto de audio',
    }
    : {
      valor: narrando ? 'narrando…' : narrMeta.label,
      tone: narrando ? 'text-cyan' : narrMeta.text,
      title: 'escribir o leer el guion, narrarlo con la voz elegida o subir tu grabación',
    }

  const tema = resumen?.tema || null
  const efectos = resumen?.efectos || 0

  return (
    <div className="mt-1 flex flex-wrap items-center gap-2 rounded-md border border-line/60 bg-canvas/40 px-2.5 py-1.5">
      <span className="eyebrow shrink-0">Audio</span>

      <Chip icon={Mic} nombre="voz" valor={voz.valor} tone={voz.tone}
        title={voz.title} onClick={onVoz} />
      <Chip icon={Music2} nombre="música"
        valor={cargando ? '…' : (tema || 'ninguna')}
        tone={tema ? 'text-ok' : 'text-muted'}
        title={tema
          ? `cama musical «${tema}» a ${resumen.db} dB`
          : 'este clip no lleva cama musical'}
        onClick={onMezcla} />
      <Chip icon={AudioLines} nombre="sfx"
        valor={cargando ? '…' : (efectos ? `${efectos} efecto${efectos === 1 ? '' : 's'}` : 'ninguno')}
        tone={efectos ? 'text-ok' : 'text-muted'}
        title={efectos
          ? `${efectos} efecto${efectos === 1 ? '' : 's'} de la paleta en la cama de sonido`
          : 'este clip no lleva efectos de sonido'}
        onClick={onMezcla} />

      {/* Cómo está la MEZCLA, que es otra cosa que lo que hay elegido. Se
          calla en dos casos: sin manifiesto no hay mezcla de la que hablar
          (y decir «sin audio» al lado de tres «ninguna» sería repetirse), y
          `sin_render` ya lo dice el distintivo de estado del clip, dos
          líneas más arriba. Se le quita el «audio » del principio porque la
          fila ya se llama así. */}
      {MEZCLA_VISIBLE.has(clip.audio?.estado) && audioMeta && (
        <span className={cn('font-mono text-[11px] uppercase tracking-wide', audioMeta.text)}
          title="estado de la mezcla sobre el mp4 que sirve la app">
          {audioMeta.label.replace(/^audio /, '')}
        </span>
      )}

      {!esPromo && narr && !narrando && (
        <>
          {narr.has_audio && (
            <audio controls preload="none" src={narracionAudioUrl(projectId, clip.id)}
              aria-label={`narración de ${clip.title}`} className="h-8 min-w-0 max-w-[280px] flex-1" />
          )}
          {narr.audio_s != null && (
            <span className="font-mono text-[11px] text-muted">
              {narr.audio_s} s · {narr.origen === 'subido' ? 'grabación propia' : (narr.voz || '')}
            </span>
          )}
          {narr.aviso_largo && (
            <span className="text-[11px] text-warn"
              title="mux.sh la acelera con atempo al montar; no se corta">
              ⚠ más larga que el video
            </span>
          )}
          <Button size="xs" variant="ghost" onClick={onNarrar} disabled={narrBusy || !narrEnabled}
            aria-label="regenerar narración"
            title={narrEnabled ? 'regenerar la narración de este clip' : 'ningún proveedor de voz disponible'}>
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </>
      )}
    </div>
  )
}
