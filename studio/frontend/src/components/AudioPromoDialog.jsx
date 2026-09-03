// Audio de una pieza — la cama de sonido y, en un promo, la voz.
//
// Un promo no lleva subtítulos: si no suena, no comunica. Hasta el sprint P2
// el sonido se montaba fuera, a mano, con `studio/tools/sfx.py`.
//
// Dos decisiones de forma que vienen de haber hecho los diez primeros a mano:
//
//   - los sonidos son un DESPLEGABLE, no texto libre: la mezcla solo sabe
//     sintetizar los de la paleta, y un nombre inventado falla dentro del
//     contenedor, tarde y con un KeyError;
//   - los avisos se calculan y se enseñan SIEMPRE (cuánta voz cabe, si la voz
//     se pega al final). Son los dos errores que ya se cometieron y que no se
//     ven hasta escuchar el resultado.
//
// Sprint E3: la cama también es de los CURSOS, y ahí no hay voz — la narración
// sale de «Generar narración» y la película la pega al montar. Y los sonidos
// se pueden OÍR antes de elegirlos (botón ▶ en cada línea): elegir «sting» o
// «subrayado» por el nombre era adivinar.
//
// Sprint R2: además de los efectos sueltos, la pieza puede llevar una CAMA
// MUSICAL — un tema con tonalidad, pulso y progresión, sintetizado por
// `musica.py`. Va en su propia sección porque es una decisión distinta: los
// efectos marcan momentos, la música sostiene la pieza entera.

import { useCallback, useEffect, useRef, useState } from 'react'
import { CheckCircle2, Loader2, Mic, Music, Play, Plus, Trash2, Volume2 } from 'lucide-react'
import { api, frameVerificacionUrl, sfxUrl } from '../api.js'
import MusicaSelector from './MusicaSelector.jsx'
import { Button } from './ui/button.jsx'
import { Input } from './ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

// Un solo <audio> para todo el diálogo: dos efectos sonando a la vez no se
// distinguen, y crear uno por línea deja objetos vivos al cerrar.
function useAudicion() {
  const [sonando, setSonando] = useState('')
  const ref = useRef(null)
  useEffect(() => () => { ref.current?.pause() }, [])
  const oir = useCallback((nombre) => {
    ref.current?.pause()
    const a = new Audio(sfxUrl(nombre))
    ref.current = a
    a.addEventListener('ended', () => setSonando(''))
    a.addEventListener('error', () => setSonando(''))
    a.play().then(() => setSonando(nombre)).catch(() => setSonando(''))
  }, [])
  return { sonando, oir }
}

const textareaCls = 'w-full resize-y rounded-md border border-line bg-canvas px-2.5 py-1.5 text-[13px] text-ink placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan'

export const VERIF_META = {
  sin_render: { label: 'sin render', text: 'text-muted' },
  sin_verificar: { label: 'sin verificar', text: 'text-muted' },
  desactualizada: { label: 'verificación vieja', text: 'text-warn' },
  al_dia: { label: 'verificado', text: 'text-ok' },
}

export const AUDIO_META = {
  sin_manifiesto: { label: 'sin audio', text: 'text-muted' },
  sin_render: { label: 'audio sin render', text: 'text-muted' },
  sin_mezclar: { label: 'sin mezclar', text: 'text-warn' },
  desactualizado: { label: 'audio desactualizado', text: 'text-warn' },
  al_dia: { label: 'con audio', text: 'text-ok' },
}

function num(valor, porDefecto = 0) {
  const n = Number.parseFloat(valor)
  return Number.isFinite(n) ? n : porDefecto
}

/** Manifiesto del backend → estado plano del formulario. */
function aFormulario(m) {
  return {
    eventos: (m.audio.eventos || []).map(([sonido, t, db]) => ({ sonido, t, db })),
    secciones: (m.voz.secciones || []).map((s) => ({ ...s })),
    voz: m.voz.voz,
    pico_db: m.audio.pico_db,
    pico_db_con_voz: m.audio.pico_db_con_voz,
    fade_in: m.audio.fade_in,
    musica: m.audio.musica || null,
  }
}

export default function AudioPromoDialog({ projectId, clip, onOpenChange, onSaved }) {
  const { sonando, oir } = useAudicion()
  const [banco, setBanco] = useState(null)
  const [datos, setDatos] = useState(null)   // respuesta completa del backend
  const [form, setForm] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')

  const cargar = useCallback(async () => {
    try {
      const d = await api.getAudioPromo(projectId, clip.id)
      setDatos(d)
      setForm(aFormulario(d.manifiesto))
    } catch (err) {
      setError(err.message)
    }
  }, [projectId, clip.id])

  useEffect(() => { cargar() }, [cargar])

  // Que efectos se pueden OIR. Es un estado del servidor, no del clip: se
  // sintetizan una vez y valen para siempre (la sintesis es determinista).
  useEffect(() => { api.getSfx().then(setBanco).catch(() => setBanco(null)) }, [])

  const guardar = async () => {
    setBusy('guardar'); setError('')
    try {
      const d = await api.putAudioPromo(projectId, clip.id, {
        eventos: form.eventos.map((e) => ({ sonido: e.sonido, t: num(e.t), db: num(e.db, -14) })),
        secciones: form.secciones
          .filter((s) => s.texto.trim())
          .map((s) => ({ t_inicio: num(s.t_inicio), texto: s.texto.trim() })),
        voz: form.voz,
        pico_db: num(form.pico_db, -3),
        pico_db_con_voz: num(form.pico_db_con_voz, -16),
        fade_in: num(form.fade_in, 0.35),
        // null = sin música. El backend lo trata igual que la ausencia de la
        // clave, así que quitarla es dejar el desplegable en «sin música».
        musica: form.musica,
      })
      setDatos(d)
      setForm(aFormulario(d.manifiesto))
      onSaved?.()
      return true
    } catch (err) {
      setError(err.message)
      return false
    } finally {
      setBusy('')
    }
  }

  // Mezclar guarda primero: nadie quiere oír una mezcla de lo que había antes.
  const mezclar = async () => {
    if (!(await guardar())) return
    setBusy('mezclar'); setError('')
    try {
      const d = await api.mezclarAudioPromo(projectId, clip.id)
      setDatos(d)
      onSaved?.()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy('')
    }
  }

  const verificar = async () => {
    setBusy('verificar'); setError('')
    try {
      setDatos(await api.verificarPromo(projectId, clip.id))
      onSaved?.()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy('')
    }
  }

  const conVoz = Boolean(form?.secciones.some((s) => s.texto.trim()))
  const meta = AUDIO_META[datos?.estado?.estado] || AUDIO_META.sin_manifiesto

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent className="p-0">
        <div className="flex items-center justify-between gap-2 border-b border-line px-4 py-3 pr-12">
          <DialogTitle className="truncate font-display text-[15px] text-ink">
            Audio · {clip.title}
          </DialogTitle>
          <span className={cn('shrink-0 font-mono text-[11px]', meta.text)}>{meta.label}</span>
        </div>

        {!form ? (
          <p className="p-4 text-[13px] text-muted">
            {error ? <span role="alert" className="text-warn">{error}</span> : 'Cargando…'}
          </p>
        ) : (
          <div className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto p-4">
            {/* — la cama — */}
            <section className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <Music className="h-3.5 w-3.5 text-accent" />
                <span className="eyebrow">Cama de sonido</span>
                <span className="ml-auto font-mono text-[11px] text-faint">
                  {datos.duracion_video ? `${datos.duracion_video.toFixed(2)} s de video` : 'sin render'}
                </span>
              </div>
              {form.eventos.length === 0 && (
                <p className="text-[12px] text-faint">
                  {datos.tipo === 'curso'
                    ? 'Sin sonidos todavía. Un clip de curso pide poco: un acento en el momento que importa y, si la escena es larga, un pad que la sostenga por debajo de la voz.'
                    : 'Sin sonidos todavía. Un promo suele llevar 4-7: una entrada, un par de acentos en los momentos que importan y un cierre.'}
                </p>
              )}
              {form.eventos.map((ev, i) => (
                <div key={i} className="flex flex-wrap items-center gap-1.5">
                  <Select value={ev.sonido}
                    onValueChange={(v) => setForm((f) => ({
                      ...f, eventos: f.eventos.map((e, j) => (i === j ? { ...e, sonido: v } : e)),
                    }))}>
                    <SelectTrigger className="h-8 w-[160px] text-[12px]"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {datos.sonidos.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <Button size="xs" variant="ghost" onClick={() => oir(ev.sonido)}
                    disabled={banco ? !banco.listos.includes(ev.sonido) : false}
                    aria-label={`oír ${ev.sonido}`}
                    title={banco && !banco.listos.includes(ev.sonido)
                      ? 'el banco todavía no está sintetizado'
                      : `oír ${ev.sonido}`}>
                    {sonando === ev.sonido
                      ? <Volume2 className="h-3.5 w-3.5 text-accent" />
                      : <Play className="h-3.5 w-3.5" />}
                  </Button>
                  <label className="flex items-center gap-1 text-[11.5px] text-muted">
                    en
                    <Input value={ev.t} inputMode="decimal" aria-label="instante en segundos"
                      onChange={(e) => setForm((f) => ({
                        ...f, eventos: f.eventos.map((x, j) => (i === j ? { ...x, t: e.target.value } : x)),
                      }))}
                      className="h-8 w-[72px] text-right font-mono text-[12px]" />
                    s
                  </label>
                  <label className="flex items-center gap-1 text-[11.5px] text-muted">
                    a
                    <Input value={ev.db} inputMode="decimal" aria-label="nivel en dB"
                      onChange={(e) => setForm((f) => ({
                        ...f, eventos: f.eventos.map((x, j) => (i === j ? { ...x, db: e.target.value } : x)),
                      }))}
                      className="h-8 w-[72px] text-right font-mono text-[12px]" />
                    dB
                  </label>
                  <Button size="xs" variant="ghost" aria-label={`quitar ${ev.sonido}`}
                    onClick={() => setForm((f) => ({
                      ...f, eventos: f.eventos.filter((_, j) => j !== i),
                    }))}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              ))}
              <div className="flex flex-wrap items-center gap-1.5">
                <Button size="xs" variant="default"
                  onClick={() => setForm((f) => ({
                    ...f,
                    eventos: [...f.eventos, { sonido: datos.sonidos[0], t: 0, db: -14 }],
                  }))}>
                  <Plus className="h-3.5 w-3.5" /> Añadir sonido
                </Button>
                {banco && !banco.completo && (
                  <Button size="xs" variant="ghost" disabled={banco.generando}
                    onClick={async () => {
                      setBanco({ ...banco, generando: true })
                      try { await api.generarSfx() } catch { /* se ve en el estado */ }
                      api.getSfx().then(setBanco).catch(() => {})
                    }}
                    title="sintetiza los wavs de la paleta para poder oírlos">
                    {banco.generando
                      ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      : <Volume2 className="h-3.5 w-3.5" />}
                    Sintetizar el banco de sonidos
                  </Button>
                )}
              </div>
            </section>

            {/* — la música — la cama que sostiene la pieza entera. Aparte de
                los efectos: aquellos marcan momentos, esta no marca nada. */}
            <section className="flex flex-col gap-2 border-t border-line pt-3">
              <div className="flex items-center gap-2">
                <Music className="h-3.5 w-3.5 text-accent" />
                <span className="eyebrow">Música</span>
                <span className="ml-auto font-mono text-[11px] text-faint">
                  {form.musica ? form.musica.tema : 'sin cama musical'}
                </span>
              </div>
              <MusicaSelector valor={form.musica} temas={datos.temas || []}
                dbDefecto={datos.musica_db ?? -24}
                onChange={(v) => setForm((f) => ({ ...f, musica: v }))} />
            </section>

            {/* — la voz — solo en un promo: un curso narra por otro camino y
                dos voces sobre el mismo clip no se pueden separar despues. */}
            {datos.voz_aqui === false ? (
              <p className="border-t border-line pt-3 text-[12px] text-muted">
                La voz de un clip de curso no se escribe aquí: sale de
                «Generar narración» y la película la pega sobre esta cama al
                montar. Por eso la cama nace en −16 dB, por debajo de la voz.
              </p>
            ) : (
            <section className="flex flex-col gap-2 border-t border-line pt-3">
              <div className="flex items-center gap-2">
                <Mic className="h-3.5 w-3.5 text-accent" />
                <span className="eyebrow">Voz (opcional)</span>
                <span className="ml-auto font-mono text-[11px] text-faint">
                  {datos.silabas_por_s} sílabas/s
                </span>
              </div>
              {!datos.voz_disponible && (
                <p className="text-[12px] text-warn">
                  Sin la service account de Vertex no hay voz: la cama sí se puede mezclar.
                </p>
              )}
              {form.secciones.map((s, i) => (
                <div key={i} className="flex items-start gap-1.5">
                  <label className="flex shrink-0 items-center gap-1 pt-1.5 text-[11.5px] text-muted">
                    <Input value={s.t_inicio} inputMode="decimal" aria-label="instante de la frase"
                      onChange={(e) => setForm((f) => ({
                        ...f, secciones: f.secciones.map((x, j) => (i === j ? { ...x, t_inicio: e.target.value } : x)),
                      }))}
                      className="h-8 w-[72px] text-right font-mono text-[12px]" />
                    s
                  </label>
                  <textarea value={s.texto} rows={2} className={textareaCls}
                    placeholder="Lo que dice la voz en ese momento"
                    onChange={(e) => setForm((f) => ({
                      ...f, secciones: f.secciones.map((x, j) => (i === j ? { ...x, texto: e.target.value } : x)),
                    }))} />
                  <Button size="xs" variant="ghost" aria-label="quitar frase" className="mt-1"
                    onClick={() => setForm((f) => ({
                      ...f, secciones: f.secciones.filter((_, j) => j !== i),
                    }))}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              ))}
              <div>
                <Button size="xs" variant="default"
                  onClick={() => setForm((f) => ({
                    ...f, secciones: [...f.secciones, { t_inicio: 0, texto: '' }],
                  }))}>
                  <Plus className="h-3.5 w-3.5" /> Añadir frase
                </Button>
              </div>
            </section>
            )}

            {/* — niveles — */}
            <section className="flex flex-wrap items-center gap-3 border-t border-line pt-3">
              <Volume2 className="h-3.5 w-3.5 text-accent" />
              <label className="flex items-center gap-1 text-[11.5px] text-muted">
                Pico de la cama
                <Input value={conVoz ? form.pico_db_con_voz : form.pico_db} inputMode="decimal"
                  onChange={(e) => setForm((f) => (conVoz
                    ? { ...f, pico_db_con_voz: e.target.value }
                    : { ...f, pico_db: e.target.value }))}
                  className="h-8 w-[76px] text-right font-mono text-[12px]" />
                dBFS
              </label>
              <label className="flex items-center gap-1 text-[11.5px] text-muted">
                Entrada
                <Input value={form.fade_in} inputMode="decimal"
                  onChange={(e) => setForm((f) => ({ ...f, fade_in: e.target.value }))}
                  className="h-8 w-[70px] text-right font-mono text-[12px]" />
                s
              </label>
              <span className="text-[11.5px] text-faint">
                {datos.tipo === 'curso'
                  ? 'La narración pica en −1.5 dB: por encima de −16 la cama compite con ella.'
                  : conVoz
                    ? 'Con voz, la cama baja para no taparla.'
                    : 'La salida se funde sola al final: el bucle no puede chasquear.'}
              </span>
            </section>

            {/* — verificación medida — solo del promo: mide la costura del
                bucle y el rango 8-15 s de redes. */}
            {datos.tipo !== 'curso' && (
              <Verificacion datos={datos} busy={busy} onVerificar={verificar} />
            )}

            {/* — avisos calculados — */}
            {datos.avisos?.length > 0 && (
              <ul className="flex flex-col gap-1 rounded-md border border-warn/40 bg-warn/10 p-2.5">
                {datos.avisos.map((a, i) => (
                  <li key={i} className="text-[12.5px] text-warn">· {a}</li>
                ))}
              </ul>
            )}
            {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
          </div>
        )}

        <div className="flex flex-wrap justify-end gap-2 border-t border-line px-4 py-3">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cerrar</Button>
          <Button variant="default" onClick={guardar} disabled={!form || Boolean(busy)}>
            {busy === 'guardar' ? 'Guardando…' : 'Guardar'}
          </Button>
          <Button variant="primary" onClick={mezclar}
            disabled={!form || Boolean(busy) || !datos?.duracion_video}
            title={!datos?.duracion_video
              ? 'el clip necesita un render vigente antes de mezclar'
              : 'guarda y monta el audio sobre el video'}>
            {busy === 'mezclar'
              ? <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Mezclando…</>
              : <>Mezclar audio</>}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

/** Una comprobación: verde o ámbar, SIEMPRE con el número al lado. Un
 *  semáforo sin cifra no deja aprender nada de lo que salió mal. */
function Check({ ok, label, valor, detalle }) {
  return (
    <div className="flex min-w-[150px] flex-1 flex-col gap-0.5 rounded-md border border-line bg-canvas/40 px-2.5 py-1.5">
      <span className="flex items-center gap-1.5">
        <span className={cn('h-1.5 w-1.5 shrink-0 rounded-full', ok ? 'bg-ok' : 'bg-warn')} />
        <span className="eyebrow">{label}</span>
      </span>
      <span className={cn('font-mono text-[13px]', ok ? 'text-ink' : 'text-warn')}>{valor}</span>
      {detalle && <span className="font-mono text-[10.5px] text-faint">{detalle}</span>}
    </div>
  )
}

function Verificacion({ datos, busy, onVerificar }) {
  const v = datos.verificacion || {}
  const informe = v.informe
  const meta = VERIF_META[v.estado] || VERIF_META.sin_verificar
  return (
    <section className="flex flex-col gap-2 border-t border-line pt-3">
      <div className="flex items-center gap-2">
        <CheckCircle2 className="h-3.5 w-3.5 text-accent" />
        <span className="eyebrow">Verificación</span>
        <span className={cn('font-mono text-[11px]', meta.text)}>{meta.label}</span>
        <Button size="xs" variant="default" className="ml-auto" onClick={onVerificar}
          disabled={Boolean(busy) || !datos.duracion_video}
          title={!datos.duracion_video
            ? 'el clip necesita un render vigente'
            : 'mide el archivo que sirve la app'}>
          {busy === 'verificar'
            ? <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Midiendo…</>
            : 'Verificar'}
        </Button>
      </div>

      {!informe ? (
        <p className="text-[12px] text-faint">
          Sin medir. La costura del bucle no se juzga a ojo: el h264 deja hasta un
          0.18 % de píxeles distintos entre dos frames que en la escena son idénticos,
          así que se mide contra ese suelo.
        </p>
      ) : (
        <>
          {v.estado === 'desactualizada' && (
            <p className="text-[12px] text-warn">
              Este informe es de otro archivo (se renderizó o se mezcló después).
              Vuelve a medir.
            </p>
          )}
          <div className="flex flex-wrap gap-2">
            <Check ok={informe.bucle?.ok} label="Bucle"
              valor={informe.bucle?.sobre_piso_pct != null
                ? `${informe.bucle.sobre_piso_pct.toFixed(3)} %`
                : '—'}
              detalle={informe.bucle?.piso_pct != null
                ? `sobre el suelo del códec (${informe.bucle.piso_pct.toFixed(3)} %)`
                : null} />
            <Check ok={informe.duracion?.ok} label="Duración"
              valor={`${informe.duracion?.s} s`}
              detalle={`formato: ${informe.duracion?.min}-${informe.duracion?.max} s`} />
            {informe.audio?.tiene_audio ? (
              <Check ok={informe.audio.ok} label="Audio"
                valor={`pico ${informe.audio.pico_db} dBFS`}
                detalle={`extremos ${informe.audio.entrada_db} / ${informe.audio.salida_db} dBFS`} />
            ) : (
              <Check ok={false} label="Audio" valor="sin pista"
                detalle="un promo sin sonido no comunica" />
            )}
            <Check ok label="Archivo" valor={informe.video?.resolucion}
              detalle={`${informe.video?.fps} fps · ${informe.archivo}`} />
          </div>

          {/* El par primero|último, uno al lado del otro: el bucle se ve. */}
          {datos.job_id && informe.costura && (
            <figure className="flex flex-col gap-1">
              <img src={frameVerificacionUrl(datos.job_id, informe.costura)}
                alt="primer y último frame, uno al lado del otro"
                className="max-h-[42vh] w-full rounded-md border border-line bg-canvas object-contain" />
              <figcaption className="text-[11px] text-faint">
                Primer frame · último frame. En un bucle cerrado son el mismo dibujo.
              </figcaption>
            </figure>
          )}

          {/* La tira: mirar los frames caza lo que ningún número dice. */}
          {datos.job_id && informe.frames?.length > 0 && (
            <div className="flex gap-1.5 overflow-x-auto pb-1">
              {informe.frames.map((f) => (
                <img key={f} src={frameVerificacionUrl(datos.job_id, f)} alt={`frame ${f}`}
                  loading="lazy"
                  className="h-[120px] shrink-0 rounded border border-line bg-canvas object-contain" />
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
