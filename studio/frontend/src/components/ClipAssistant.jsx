// Asistente de clip — escribe el script de un clip a partir de un formulario.
//
// Para quien NO escribe Manim a mano. Va detras de la preferencia `guided`
// (apagada por defecto): con el modo guiado apagado este componente no se
// monta y Proyectos no enseña ni un boton de mas. El camino de siempre
// —"Añadir clip" y "Editar en Estudio"— no cambia ni un pixel.
//
// Nunca guarda a ciegas: genera, ENSEÑA el script y solo entonces ofrece
// crear el clip.

import { useEffect, useMemo, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { ArrowLeft, Sparkles, Wand2 } from 'lucide-react'
import { api } from '../api.js'
import { Button } from './ui/button.jsx'
import { Input } from './ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'
import { useEditorTheme } from '../themes.js'

const textareaCls = 'w-full resize-y rounded-md border border-line bg-canvas px-2.5 py-1.5 text-[13px] text-ink placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan'

// El estilo del proyecto ya hace `from manim import *` y despues instala una
// sombra de `Text` (arregla una trampa real de Manim 0.20). Si el script del
// clip vuelve a importar, ese `import *` REPONE el Text de manim y se pierde
// la correccion — es la trampa que documentan los cursos del repo ("los clips
// NO repiten imports"). Por eso se quitan los imports de cabecera de todo
// script que entre por aqui, y solo cuando el proyecto tiene estilo.
const RE_IMPORT = /^\s*(?:import|from)\s+\S/
const RE_DEF = /^\s*(?:class|def)\s/

export function quitarImportsDeCabecera(script) {
  const lines = script.split('\n')
  const firstDef = lines.findIndex((l) => RE_DEF.test(l))
  const limit = firstDef === -1 ? lines.length : firstDef
  let quitados = 0
  const kept = lines.map((l, i) => {
    if (i < limit && RE_IMPORT.test(l)) { quitados += 1; return null }
    return l
  }).filter((l) => l !== null)
  if (!quitados) return { script, quitados: 0 }
  // Deja constancia en el propio script de por que faltan.
  const cuerpo = kept.join('\n').replace(/^\n+/, '')
  return {
    script: `# (imports quitados: los aporta el estilo del proyecto)\n${cuerpo}`,
    quitados,
  }
}

const ORIGENES = [
  { id: 'ia', label: 'Descríbelo y lo escribe la IA' },
  { id: 'ejemplo', label: 'Partir de una animación de ejemplo' },
  { id: 'vacio', label: 'Esqueleto en blanco' },
]

export default function ClipAssistant({ open, onOpenChange, project, aiEnabled, onCreated }) {
  const temaEditor = useEditorTheme()   // CodeMirror sigue al tema de la app
  const [titulo, setTitulo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [origen, setOrigen] = useState(aiEnabled ? 'ia' : 'ejemplo')
  const [animIndex, setAnimIndex] = useState(null)
  const [animId, setAnimId] = useState('')
  const [busy, setBusy] = useState('')      // '' | 'generando' | 'creando'
  const [error, setError] = useState('')
  const [aviso, setAviso] = useState('')
  const [preview, setPreview] = useState(null)  // {script, scene}

  const n = (project?.clips?.length || 0) + 1
  const anterior = project?.clips?.length
    ? [...project.clips].sort((a, b) => a.position - b.position).at(-1)
    : null

  useEffect(() => {
    if (!open) return
    setTitulo(`${n} · `); setDescripcion(''); setError(''); setAviso('')
    setPreview(null); setBusy('')
    setOrigen(aiEnabled ? 'ia' : 'ejemplo')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  useEffect(() => {
    if (!open || animIndex) return
    api.animationsIndex()
      .then((d) => setAnimIndex(d.categories.filter((c) => c.count > 0)))
      .catch(() => setAnimIndex([]))
  }, [open, animIndex])

  const animaciones = useMemo(() => (animIndex || []).flatMap(
    (c) => c.animations.map((a) => ({ ...a, cat: c.name }))), [animIndex])

  const esqueleto = (scene) => `class ${scene}(Scene):
    def construct(self):
        titulo = titulo_curso("${(titulo.replace(/^\d+\s*·\s*/, '') || 'Título').replace(/"/g, "'")}")
        pie = pie_curso("Una frase que resuma la idea de este clip.")

        self.play(FadeIn(titulo), run_time=0.8)
        self.play(FadeIn(pie), run_time=0.6)
        self.wait(2)
`

  // Contexto real del proyecto para que la IA no invente el estilo: como se
  // llama el curso, en que clip vamos, donde termino el anterior y el tope
  // duro de duracion del formato.
  const prompt = () => [
    `Curso: "${project.name}"${project.description ? ` — ${project.description}` : ''}`,
    `Clip ${n} del curso, titulado "${titulo.trim()}".`,
    anterior?.final_state?.trim()
      ? `El clip anterior termina asi: ${anterior.final_state.trim()}. Empieza desde ese estado.`
      : 'Es el primer clip: empieza a pantalla limpia.',
    '',
    'Qué debe contar este clip:',
    descripcion.trim(),
    '',
    'Reglas duras de este proyecto:',
    `- Define UNA sola clase Scene, llamada exactamente Clip${n}.`,
    '- NO escribas imports: el estilo del proyecto ya aporta manim, numpy y la marca.',
    '- Usa los helpers del estilo: titulo_curso(), pie_curso(), formula_pie(), tag_junto().',
    '- La animación debe durar entre 28 y 45 segundos.',
    '- Nada de red ni de archivos.',
  ].join('\n')

  const generar = async () => {
    setError(''); setAviso(''); setBusy('generando')
    try {
      let script
      if (origen === 'ia') {
        const d = await api.aiGenerate({ prompt: prompt() })
        script = d.script
      } else if (origen === 'ejemplo') {
        if (!animId) throw new Error('Elige una animación de ejemplo')
        const a = await api.getAnimation(animId)
        script = a.script
      } else {
        script = esqueleto(`Clip${n}`)
      }

      if (project.style_block?.trim()) {
        const r = quitarImportsDeCabecera(script)
        script = r.script
        if (r.quitados) {
          setAviso(`Se quitaron ${r.quitados} línea${r.quitados === 1 ? '' : 's'} de import: `
            + 'las aporta el estilo del proyecto (repetirlas rompe la tipografía de marca).')
        }
      }

      // La escena real la decide el backend leyendo el AST, no una suposicion.
      const { scenes } = await api.scenes(script)
      if (!scenes.length) throw new Error('El script generado no define ninguna Scene. Prueba a describirlo de otra forma.')
      setPreview({ script, scene: scenes[0] })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy('')
    }
  }

  const crear = async () => {
    setError(''); setBusy('creando')
    try {
      await api.createClip(project.id, {
        title: titulo.trim(), scene: preview.scene, script: preview.script,
      })
      onCreated()
    } catch (err) {
      setError(err.message)
      setBusy('')
    }
  }

  const puedeGenerar = titulo.trim()
    && (origen !== 'ia' || descripcion.trim().length > 10)
    && (origen !== 'ejemplo' || animId)
    && !busy

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <div className="flex items-center gap-2 border-b border-line px-4 py-3 pr-12">
            <Wand2 className="h-4 w-4 shrink-0 text-accent" />
            <DialogTitle className="font-display text-[15px] text-ink">
              Asistente · clip {n} de «{project.name}»
            </DialogTitle>
          </div>

          {preview ? (
            <div className="flex max-h-[85vh] flex-col">
              <div className="flex flex-wrap items-center gap-2 border-b border-line px-4 py-2">
                <span className="eyebrow">Escena detectada</span>
                <span className="font-mono text-[12.5px] text-ink">{preview.scene}</span>
                <span className="ml-auto text-[12px] text-muted">
                  Revísalo antes de guardar; luego se edita en el Estudio como cualquier clip.
                </span>
              </div>
              {aviso && (
                <p role="status" className="border-b border-line bg-cyan/10 px-4 py-2 text-[12.5px] text-cyan">
                  {aviso}
                </p>
              )}
              <CodeMirror
                value={preview.script}
                extensions={[python()]}
                theme={temaEditor}
                editable={false}
                height="340px"
                className="editor min-h-0 flex-1 overflow-auto text-[13px]"
                basicSetup={{ foldGutter: false, highlightActiveLine: false }}
              />
              {error && <p role="alert" className="border-t border-line px-4 py-2 text-[13px] text-err">{error}</p>}
              <div className="flex justify-between gap-2 border-t border-line px-4 py-3">
                <Button variant="ghost" onClick={() => { setPreview(null); setAviso('') }}>
                  <ArrowLeft className="h-3.5 w-3.5" /> Volver
                </Button>
                <Button variant="primary" onClick={crear} disabled={busy === 'creando'}>
                  {busy === 'creando' ? 'Creando…' : 'Guardar como clip'}
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex max-h-[85vh] flex-col">
              <div className="flex flex-col gap-3.5 overflow-y-auto p-4">
                <label className="flex flex-col gap-1">
                  <span className="eyebrow">Título del clip</span>
                  <Input value={titulo} onChange={(e) => setTitulo(e.target.value)} autoFocus
                    maxLength={200} placeholder={`${n} · De qué va este clip`} />
                </label>

                <fieldset className="flex flex-col gap-2">
                  <legend className="eyebrow mb-1">Cómo se escribe el script</legend>
                  {ORIGENES.map((o) => {
                    const off = o.id === 'ia' && !aiEnabled
                    return (
                      <label key={o.id}
                        className={cn('flex items-center gap-2.5 text-[13px]',
                          off ? 'cursor-not-allowed text-faint' : 'cursor-pointer text-ink')}>
                        <input type="radio" name="origen" value={o.id} disabled={off}
                          checked={origen === o.id} onChange={() => setOrigen(o.id)}
                          className="h-3.5 w-3.5 accent-[var(--accent)]" />
                        {o.id === 'ia' && <Sparkles className="h-3.5 w-3.5 shrink-0 text-accent" />}
                        {o.label}
                        {off && <span className="text-[11.5px]">(requiere el asistente IA configurado)</span>}
                      </label>
                    )
                  })}
                </fieldset>

                {origen === 'ia' && (
                  <label className="flex flex-col gap-1">
                    <span className="eyebrow">Qué debe contar</span>
                    <textarea value={descripcion} onChange={(e) => setDescripcion(e.target.value)}
                      rows={4} className={textareaCls}
                      placeholder="Explica qué se ve y qué se aprende. P. ej.: «Un satélite recorre su órbita mientras se marca el punto de máxima velocidad; al final queda la fórmula de la velocidad orbital abajo.»" />
                    <span className="text-[11.5px] text-faint">
                      El asistente ya conoce el nombre del curso, en qué clip vamos, dónde
                      terminó el anterior y que el formato pide 28–45 s.
                    </span>
                  </label>
                )}

                {origen === 'ejemplo' && (
                  <label className="flex flex-col gap-1">
                    <span className="eyebrow">Animación de partida</span>
                    {animIndex == null ? (
                      <span className="text-[13px] text-muted">Cargando animaciones…</span>
                    ) : (
                      <Select value={animId} onValueChange={setAnimId}>
                        <SelectTrigger><SelectValue placeholder="Elige una animación…" /></SelectTrigger>
                        <SelectContent>
                          {animaciones.map((a) => (
                            <SelectItem key={a.id} value={a.id}>{a.cat} · {a.title}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                    <span className="text-[11.5px] text-faint">
                      Se copia su script al clip; desde ahí se edita como cualquier otro.
                      Las {animaciones.length} animaciones están en Aprender.
                    </span>
                  </label>
                )}

                {error && <p role="alert" className="text-[13px] text-err">{error}</p>}
              </div>
              <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
                <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
                <Button variant="primary" onClick={generar} disabled={!puedeGenerar}>
                  {busy === 'generando'
                    ? (origen === 'ia' ? 'Escribiendo… (puede tardar)' : 'Preparando…')
                    : 'Continuar'}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      )}
    </Dialog>
  )
}
