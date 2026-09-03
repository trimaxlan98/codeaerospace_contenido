// La cama musical de una pieza o de una película entera.
//
// Hasta el sprint R2 la app no tenía música: se ponía fuera, en un editor, y
// por eso existe `unir_vertical.py --mudo`. Ahora los ocho temas se sintetizan
// con numpy dentro del contenedor (`studio/tools/musica.py`) y se eligen aquí.
//
// Dos decisiones de forma, las mismas que en la paleta de SFX y por la misma
// razón:
//
//   - el tema es un DESPLEGABLE cerrado, no texto libre: la síntesis solo
//     conoce los del catálogo y un nombre inventado falla dentro del
//     contenedor, tarde;
//   - se puede OÍR antes de elegir (botón ▶). «deriva» y «cuerdas_frias» no
//     se distinguen leyéndolos, y cada tema trae su bpm y su carácter al lado
//     para no tener que reproducirlos los ocho.
//
// El nivel va en dB y el umbral del aviso está MEDIDO, no elegido: con la voz
// en −1.5 dBFS, la separación voz/música en el tramo hablado es 15,0 dB con la
// cama en −24 y 9,0 dB en −18. El mínimo de la casa son 12 dB, y eso se rompe
// justo en −21. Por eso el aviso salta ahí y el defecto son −24.

import { useCallback, useEffect, useRef, useState } from 'react'
import { Loader2, Music2, Play, Volume2 } from 'lucide-react'
import { api, musicaUrl } from '../api.js'
import { Button } from './ui/button.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

export const SIN_MUSICA = 'ninguno'
// Los extremos del deslizador. Por debajo de −40 la cama no se oye y por
// encima de −6 tapa cualquier cosa: fuera de ese arco no hay decisión que
// tomar. El backend acepta −60..0; esto es el rango útil.
export const DB_MIN = -40
export const DB_MAX = -6
// Espejo de `audio_promo.MUSICA_DB_AVISO`.
export const DB_AVISO = -21

/** Un solo <audio> para todo el selector: dos temas a la vez no se juzgan. */
function useAudicion() {
  const [sonando, setSonando] = useState('')
  const ref = useRef(null)
  useEffect(() => () => { ref.current?.pause() }, [])
  const oir = useCallback((tema) => {
    ref.current?.pause()
    if (sonando === tema) { setSonando(''); return }
    const a = new Audio(musicaUrl(tema))
    ref.current = a
    a.addEventListener('ended', () => setSonando(''))
    a.addEventListener('error', () => setSonando(''))
    a.play().then(() => setSonando(tema)).catch(() => setSonando(''))
  }, [sonando])
  return { sonando, oir }
}

/**
 * @param {{tema: string, db: number} | null} valor
 * @param {(v: {tema: string, db: number} | null) => void} onChange
 * @param {string[]} temas  nombres válidos (del backend); el banco añade bpm
 * @param {number} dbDefecto
 */
export default function MusicaSelector({ valor, onChange, temas = [], dbDefecto = -24 }) {
  const { sonando, oir } = useAudicion()
  const [banco, setBanco] = useState(null)
  const [generando, setGenerando] = useState(false)

  // El banco es estado del SERVIDOR, no de la pieza: los wavs se sintetizan
  // una vez (la síntesis es determinista) y valen para siempre.
  useEffect(() => { api.getMusica().then(setBanco).catch(() => setBanco(null)) }, [])

  const nombres = banco?.temas?.map((t) => t.nombre) || temas
  const info = banco?.temas?.find((t) => t.nombre === valor?.tema)
  const listo = banco ? banco.listos.includes(valor?.tema) : false
  const db = valor?.db ?? dbDefecto

  const generar = async () => {
    setGenerando(true)
    try { await api.generarMusica() } catch { /* se ve en el estado */ }
    api.getMusica().then(setBanco).catch(() => {})
    setGenerando(false)
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-1.5">
        <Music2 className="h-3.5 w-3.5 shrink-0 text-accent" />
        <Select
          value={valor?.tema || SIN_MUSICA}
          onValueChange={(v) => onChange(v === SIN_MUSICA ? null : { tema: v, db })}>
          <SelectTrigger className="h-8 w-[172px] text-[12px]"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value={SIN_MUSICA}>sin música</SelectItem>
            {nombres.map((n) => <SelectItem key={n} value={n}>{n}</SelectItem>)}
          </SelectContent>
        </Select>

        {valor?.tema && (
          <Button size="xs" variant="ghost" onClick={() => oir(valor.tema)}
            disabled={banco ? !listo : false}
            aria-label={`oír ${valor.tema}`}
            title={banco && !listo
              ? 'el banco de música todavía no está sintetizado'
              : `oír ${valor.tema}`}>
            {sonando === valor.tema
              ? <Volume2 className="h-3.5 w-3.5 text-accent" />
              : <Play className="h-3.5 w-3.5" />}
          </Button>
        )}

        {valor?.tema && (
          <label className="flex flex-1 items-center gap-1.5 text-[11.5px] text-muted">
            <input type="range" min={DB_MIN} max={DB_MAX} step={1} value={db}
              aria-label="nivel de la música en dB"
              onChange={(e) => onChange({ tema: valor.tema, db: Number(e.target.value) })}
              className="h-1.5 min-w-[96px] flex-1 cursor-pointer rounded-full accent-[var(--accent)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan" />
            <span className={cn('w-[52px] shrink-0 text-right font-mono',
              db > DB_AVISO ? 'text-warn' : 'text-ink')}>
              {db} dB
            </span>
          </label>
        )}

        {banco && !banco.completo && (
          <Button size="xs" variant="ghost" onClick={generar} disabled={generando}
            title="sintetiza una vista previa de 12 s por tema para poder oírlos">
            {generando
              ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
              : <Volume2 className="h-3.5 w-3.5" />}
            Sintetizar la música
          </Button>
        )}
      </div>

      {info && (
        <p className="text-[11.5px] text-faint">
          <span className="font-mono">{info.bpm} bpm · {info.caracter}</span>
          {info.descripcion ? ` — ${info.descripcion}` : ''}
        </p>
      )}
      {valor?.tema && db > DB_AVISO && (
        <p role="status" className="text-[12px] text-warn">
          Por encima de {DB_AVISO} dB la cama compite con la voz, que pica en
          −1.5 dB. Medido sobre un promo: la voz queda 15,0 dB por encima de la
          música a −24 dB y solo 9,0 dB a −18.
        </p>
      )}
    </div>
  )
}
