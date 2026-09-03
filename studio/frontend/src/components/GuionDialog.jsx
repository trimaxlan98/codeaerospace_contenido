// Guion de un clip: se LEE, se ESCRIBE y se NARRA desde aqui.
//
// Antes era un lector del texto que generaba Vertex. Desde R1 (voz sin GCP)
// el guion es una tabla de secciones cronometradas {t_inicio, t_fin,
// momento, texto} que el dueño (o Claude) escribe a mano cuando Gemini no
// esta, y que cualquier proveedor de voz habla alineando cada seccion a su
// instante. Tambien es la puerta de la GRABACION PROPIA: se sube un
// wav/mp3/m4a y queda como la narracion del clip.

import { useEffect, useRef, useState } from 'react'
import { Loader2, Mic, Plus, Save, Trash2, Upload } from 'lucide-react'
import { api, narracionAudioUrl } from '../api.js'
import { Button } from './ui/button.jsx'
import { Input } from './ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import VozSelector from './VozSelector.jsx'
import { cn } from '@/lib/utils'

const ACEPTA = '.wav,.mp3,.flac,.ogg,.m4a,.aac,.webm,.opus'

function fila(t0 = 0, t1 = 0) {
  return { t_inicio: t0, t_fin: t1, momento: '', texto: '' }
}

// Palabras por segundo de una narracion pausada (misma cifra que el backend).
const PALABRAS_POR_S = 2.2

export default function GuionDialog({ projectId, clip, narr, narracion, voz, onVoz, onOpenChange, onChanged }) {
  const [secciones, setSecciones] = useState([])
  const [existe, setExiste] = useState(false)
  const [videoS, setVideoS] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [busy, setBusy] = useState('') // guardar | narrar | subir
  const [error, setError] = useState('')
  const [aviso, setAviso] = useState('')
  const [sucio, setSucio] = useState(false)
  const fileRef = useRef(null)
  const open = Boolean(clip)

  useEffect(() => {
    if (!clip) return
    setCargando(true); setError(''); setAviso(''); setSucio(false)
    let alive = true
    api.getGuion(projectId, clip.id).then((d) => {
      if (!alive) return
      setSecciones(d.secciones?.length ? d.secciones : [fila(0, d.video_s || 0)])
      setExiste(d.existe)
      setVideoS(d.video_s)
    }).catch((err) => { if (alive) setError(err.message) })
      .finally(() => { if (alive) setCargando(false) })
    return () => { alive = false }
  }, [projectId, clip])

  const palabras = secciones.reduce((n, s) => n + (s.texto || '').trim().split(/\s+/).filter(Boolean).length, 0)
  const cabe = videoS ? palabras <= videoS * PALABRAS_POR_S : true

  const set = (i, campo, valor) => {
    setSucio(true)
    setSecciones((prev) => prev.map((s, j) => (j === i ? { ...s, [campo]: valor } : s)))
  }
  const quitar = (i) => { setSucio(true); setSecciones((prev) => prev.filter((_, j) => j !== i)) }
  const anadir = () => {
    setSucio(true)
    setSecciones((prev) => {
      const ult = prev[prev.length - 1]
      const t0 = ult ? Number(ult.t_fin || ult.t_inicio || 0) : 0
      return [...prev, fila(t0, t0)]
    })
  }

  const normalizadas = () => secciones
    .filter((s) => (s.texto || '').trim())
    .map((s) => ({ t_inicio: Number(s.t_inicio) || 0, t_fin: Number(s.t_fin) || Number(s.t_inicio) || 0,
      momento: s.momento || '', texto: s.texto.trim() }))

  const guardar = async () => {
    setBusy('guardar'); setError(''); setAviso('')
    try {
      const r = await api.putGuion(projectId, clip.id, normalizadas())
      setExiste(true); setSucio(false)
      setAviso(`Guion guardado · ${r.palabras} palabras`)
      onChanged?.()
      return true
    } catch (err) { setError(err.message); return false } finally { setBusy('') }
  }

  const narrar = async () => {
    if (sucio || !existe) { const ok = await guardar(); if (!ok) return }
    setBusy('narrar'); setError(''); setAviso('')
    try {
      await api.startNarracion(projectId, {
        clips: [clip.id], force: true, solo_audio: true,
        proveedor: voz?.proveedor || undefined, voz: voz?.voz || undefined,
      })
      setAviso('Narrando este guion… el audio aparece en la tarjeta del clip al terminar.')
      onChanged?.()
    } catch (err) { setError(err.message) } finally { setBusy('') }
  }

  const subir = async (file) => {
    if (!file) return
    setBusy('subir'); setError(''); setAviso('')
    try {
      const r = await api.subirNarracion(projectId, clip.id, file)
      setAviso(`Grabación registrada · ${r.audio_s} s${r.video_s ? ` (video ${r.video_s} s)` : ''}`)
      onChanged?.()
    } catch (err) { setError(err.message) } finally { setBusy(''); if (fileRef.current) fileRef.current.value = '' }
  }

  const proveedores = narracion?.proveedores || []
  const puedeNarrar = Boolean(narracion?.enabled) && Boolean(voz?.proveedor)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {clip && (
        <DialogContent className="max-w-3xl p-0">
          <div className="border-b border-line px-4 py-3 pr-12">
            <DialogTitle className="truncate font-display text-[15px] text-ink">
              Guion y voz · {clip.title}
            </DialogTitle>
            <p className="mt-0.5 text-[12px] text-muted">
              {videoS ? `Video de ${videoS} s · caben ~${Math.floor(videoS * PALABRAS_POR_S)} palabras` : 'Sin render: la duración se conocerá al renderizar'}
              {' · '}<span className={cn(cabe ? 'text-muted' : 'text-warn')}>{palabras} escritas</span>
            </p>
          </div>

          <div className="max-h-[62vh] overflow-y-auto p-4">
            {cargando ? (
              <p className="text-[13px] text-muted">Cargando guion…</p>
            ) : (
              <table className="w-full border-collapse text-[13px]">
                <thead>
                  <tr className="text-left font-mono text-[10.5px] uppercase tracking-wide text-faint">
                    <th className="w-[72px] pb-1 pr-2">inicio s</th>
                    <th className="w-[72px] pb-1 pr-2">fin s</th>
                    <th className="w-[150px] pb-1 pr-2">momento visual</th>
                    <th className="pb-1 pr-2">narración</th>
                    <th className="w-8 pb-1" />
                  </tr>
                </thead>
                <tbody>
                  {secciones.map((s, i) => (
                    <tr key={i} className="align-top">
                      <td className="py-1 pr-2">
                        <Input type="number" min="0" step="0.1" value={s.t_inicio} aria-label={`inicio de la sección ${i + 1}`}
                          onChange={(e) => set(i, 't_inicio', e.target.value)} className="h-8 px-2 font-mono text-[12px]" />
                      </td>
                      <td className="py-1 pr-2">
                        <Input type="number" min="0" step="0.1" value={s.t_fin} aria-label={`fin de la sección ${i + 1}`}
                          onChange={(e) => set(i, 't_fin', e.target.value)} className="h-8 px-2 font-mono text-[12px]" />
                      </td>
                      <td className="py-1 pr-2">
                        <Input value={s.momento} placeholder="qué se ve" aria-label={`momento de la sección ${i + 1}`}
                          onChange={(e) => set(i, 'momento', e.target.value)} className="h-8 px-2 text-[12px]" />
                      </td>
                      <td className="py-1 pr-2">
                        <textarea value={s.texto} rows={2} aria-label={`texto de la sección ${i + 1}`}
                          placeholder="Frases cortas, sin fórmulas en notación: «zeta al cuadrado más c»."
                          onChange={(e) => set(i, 'texto', e.target.value)}
                          className="w-full resize-y rounded-md border border-line bg-canvas px-2 py-1.5 text-[13px] leading-snug text-ink placeholder:text-faint focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan" />
                      </td>
                      <td className="py-1">
                        <Button size="xs" variant="ghost" onClick={() => quitar(i)} aria-label={`quitar la sección ${i + 1}`}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <Button size="xs" variant="ghost" onClick={anadir} className="mt-1">
              <Plus className="h-3.5 w-3.5" /> Sección
            </Button>

            {narr?.has_audio && (
              <div className="mt-3 flex flex-wrap items-center gap-2 rounded-md border border-line/60 bg-canvas/40 px-2.5 py-1.5">
                <Mic className="h-3.5 w-3.5 text-accent" />
                <span className="font-mono text-[11px] uppercase tracking-wide text-muted">
                  {narr.origen === 'subido' ? 'grabación propia' : `${narr.proveedor || 'tts'} · ${narr.voz || ''}`}
                </span>
                <audio controls preload="none" src={narracionAudioUrl(projectId, clip.id)}
                  aria-label={`narración de ${clip.title}`} className="h-8 min-w-0 max-w-[320px] flex-1" />
                {narr.audio_s != null && <span className="font-mono text-[11px] text-muted">{narr.audio_s} s</span>}
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2 border-t border-line px-4 py-3">
            <Button size="sm" variant="default" onClick={guardar} disabled={Boolean(busy) || cargando}>
              {busy === 'guardar' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />} Guardar guion
            </Button>
            <VozSelector proveedores={proveedores} value={voz} onChange={onVoz} disabled={Boolean(busy)} compact />
            <Button size="sm" variant="default" onClick={narrar} disabled={Boolean(busy) || cargando || !puedeNarrar}
              title={puedeNarrar ? 'sintetiza este guion con la voz elegida (no lo reescribe)' : 'ningún proveedor de voz disponible'}>
              {busy === 'narrar' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Mic className="h-3.5 w-3.5" />} Narrar este guion
            </Button>
            <span className="mx-1 text-faint">·</span>
            <input ref={fileRef} type="file" accept={ACEPTA} className="sr-only" id={`voz-${clip.id}`}
              onChange={(e) => subir(e.target.files?.[0])} />
            <Button size="sm" variant="ghost" asChild disabled={Boolean(busy)}>
              <label htmlFor={`voz-${clip.id}`} className="cursor-pointer"
                title="tu propia grabación (wav, mp3, m4a…): se recorta el silencio y queda como la narración del clip">
                {busy === 'subir' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Upload className="h-3.5 w-3.5" />} Subir grabación
              </label>
            </Button>
            {error && <span role="alert" className="text-[12.5px] text-warn">{error}</span>}
            {!error && aviso && <span className="text-[12.5px] text-ok">{aviso}</span>}
          </div>
        </DialogContent>
      )}
    </Dialog>
  )
}
