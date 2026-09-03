// Importar un proyecto COMO ARCHIVOS (sprint R3a).
//
// Hasta ahora un curso nuevo nacía en la terminal: `subir_curso.py` leía
// `studio/content/cursos/<slug>/` y lo metía en la base. Este diálogo pone
// ese mismo camino en la app, por las dos puertas que tienen sentido:
//
//   · un .zip de fuentes (el que produce «Fuentes (.zip)» en cualquier
//     proyecto — ida y vuelta byte a byte);
//   · un directorio del repo, por slug y origen (cursos, verticales, promos).
//
// «Comprobar» es el `--dry-run` del CLI: valida y enseña el plan sin escribir.

import { useEffect, useState } from 'react'
import { FileUp, FolderGit2, Upload } from 'lucide-react'
import { api } from '../api.js'
import { Button } from './ui/button.jsx'
import { Input } from './ui/input.jsx'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx'
import { cn } from '@/lib/utils'

const ORIGENES = [
  { id: 'cursos', label: 'Cursos (16:9)', hint: 'curso.json + style_block.py + clips/NN-*.py' },
  { id: 'verticales', label: 'Verticales (9:16)', hint: 'curso.json con piezas; cada pieza es un clip' },
  { id: 'promos', label: 'Promos de redes', hint: 'promo.json; un proyecto de un solo clip' },
]

const MODOS = [
  { id: 'zip', nombre: 'Archivo .zip', resumen: 'Las fuentes exportadas de un proyecto.', icon: FileUp },
  { id: 'repo', nombre: 'Del repositorio', resumen: 'Un directorio de studio/content/.', icon: FolderGit2 },
]

export default function ImportarDialog({ open, onOpenChange, onImported }) {
  const [modo, setModo] = useState('zip')
  const [file, setFile] = useState(null)
  const [origen, setOrigen] = useState('cursos')
  const [slug, setSlug] = useState('')
  const [importables, setImportables] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')

  useEffect(() => {
    if (!open) return
    setModo('zip'); setFile(null); setSlug(''); setOrigen('cursos')
    setResultado(null); setError(''); setBusy('')
    // El índice de lo que hay en el repo no puede tumbar el diálogo: sin él
    // el slug sigue escribiéndose a mano.
    api.importables().then(setImportables).catch(() => setImportables(null))
  }, [open])

  const slugs = importables?.origenes?.[origen] || []

  const lanzar = async (dryRun) => {
    if (busy) return
    setBusy(dryRun ? 'comprobar' : 'importar')
    setError('')
    setResultado(null)
    try {
      const res = modo === 'zip'
        ? await api.importarZip(file, dryRun)
        : await api.importarDelRepo(slug.trim(), origen, dryRun)
      setResultado(res)
      if (!dryRun && res.project_id) onImported?.(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy('')
    }
  }

  const listo = modo === 'zip' ? Boolean(file) : Boolean(slug.trim())

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <DialogContent className="p-0">
          <div className="flex max-h-[85vh] flex-col">
            <div className="border-b border-line px-4 py-3 pr-12">
              <DialogTitle className="font-display text-[15px] text-ink">Importar proyecto</DialogTitle>
              <p className="mt-1 text-[12px] leading-snug text-muted">
                Un proyecto es un directorio: <code>curso.json</code> +{' '}
                <code>style_block.py</code> + un <code>.py</code> por clip. Es
                el mismo formato que lee <code>subir_curso.py</code> en la terminal.
              </p>
            </div>

            <div className="flex flex-col gap-3 overflow-y-auto p-4">
              <div className="flex flex-col gap-1.5">
                <span className="eyebrow">De dónde</span>
                <div role="radiogroup" aria-label="origen de la importación"
                  className="grid grid-cols-[repeat(auto-fit,minmax(170px,1fr))] gap-2">
                  {MODOS.map((m) => {
                    const on = m.id === modo
                    const Icon = m.icon
                    return (
                      <button key={m.id} type="button" role="radio" aria-checked={on}
                        onClick={() => { setModo(m.id); setResultado(null); setError('') }}
                        className={cn(
                          'flex flex-col gap-1 rounded-lg border p-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan',
                          on ? 'border-accent bg-surface-2' : 'border-line hover:border-line-strong',
                        )}>
                        <span className={cn('flex items-center gap-1.5 text-[13px] font-semibold',
                          on ? 'text-accent' : 'text-ink')}>
                          <Icon className="h-3.5 w-3.5" aria-hidden="true" /> {m.nombre}
                        </span>
                        <span className="text-[11.5px] leading-snug text-muted">{m.resumen}</span>
                      </button>
                    )
                  })}
                </div>
              </div>

              {modo === 'zip' ? (
                <label className="flex flex-col gap-1">
                  <span className="eyebrow">Archivo de fuentes</span>
                  <input type="file" accept=".zip,application/zip"
                    onChange={(e) => { setFile(e.target.files?.[0] || null); setResultado(null) }}
                    aria-label="zip de fuentes"
                    className="block w-full text-[12.5px] text-muted file:mr-3 file:rounded-md file:border file:border-line file:bg-surface-2 file:px-2.5 file:py-1.5 file:text-[12.5px] file:text-ink hover:file:border-line-strong" />
                  <span className="text-[11.5px] text-faint">
                    Máximo 5 MB. Se importa por nombre exacto: si ya existe un
                    proyecto con ese nombre, se actualiza (nunca se borran clips).
                  </span>
                </label>
              ) : (
                <>
                  <label className="flex flex-col gap-1">
                    <span className="eyebrow">Origen</span>
                    <Select value={origen} onValueChange={(v) => { setOrigen(v); setSlug(''); setResultado(null) }}>
                      <SelectTrigger className="max-w-[280px]"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {ORIGENES.map((o) => <SelectItem key={o.id} value={o.id}>{o.label}</SelectItem>)}
                      </SelectContent>
                    </Select>
                    <span className="text-[11.5px] text-faint">
                      {ORIGENES.find((o) => o.id === origen)?.hint}
                    </span>
                  </label>
                  <label className="flex flex-col gap-1">
                    <span className="eyebrow">Directorio</span>
                    {slugs.length > 0 ? (
                      <Select value={slug} onValueChange={(v) => { setSlug(v); setResultado(null) }}>
                        <SelectTrigger className="max-w-[420px]" aria-label="directorio del repositorio">
                          <SelectValue placeholder="Elige uno…" />
                        </SelectTrigger>
                        <SelectContent>
                          {slugs.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    ) : (
                      <Input value={slug} onChange={(e) => setSlug(e.target.value)}
                        placeholder="mi-curso-nuevo" aria-label="slug del directorio"
                        className="max-w-[420px] font-mono text-[12.5px]" />
                    )}
                    <span className="text-[11.5px] text-faint">
                      {importables
                        ? `${slugs.length} disponible${slugs.length === 1 ? '' : 's'} en ${importables.content_dir}/${origen}/`
                        : 'Nombre del directorio dentro de studio/content/.'}
                    </span>
                  </label>
                </>
              )}

              {resultado && (
                <div className="flex flex-col gap-1.5 rounded-lg border border-line bg-surface-2 p-3">
                  <span className={cn('text-[13px] font-semibold',
                    resultado.dry_run ? 'text-cyan' : 'text-ok')}>
                    {resultado.dry_run ? 'Plan (no se ha escrito nada)' : 'Importado'}
                    {': '}{resultado.name}
                  </span>
                  <span className="font-mono text-[11.5px] text-muted">
                    {resultado.creado ? 'proyecto nuevo' : 'proyecto existente'}
                    {' · '}{resultado.clips} clip{resultado.clips === 1 ? '' : 's'}
                    {' · '}{resultado.creados} nuevo{resultado.creados === 1 ? '' : 's'}
                    {' · '}{resultado.actualizados} actualizado{resultado.actualizados === 1 ? '' : 's'}
                    {resultado.stale > 0 && ` · ${resultado.stale} por re-renderizar`}
                    {resultado.guiones > 0 && ` · ${resultado.guiones} guion${resultado.guiones === 1 ? '' : 'es'}`}
                  </span>
                  <pre className="max-h-40 overflow-auto whitespace-pre-wrap break-words font-mono text-[11px] leading-snug text-muted">
                    {(resultado.reporte || []).join('\n')}
                  </pre>
                </div>
              )}
              {error && <p role="alert" className="text-[13px] text-warn">{error}</p>}
            </div>

            <div className="flex justify-end gap-2 border-t border-line px-4 py-3">
              <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>Cerrar</Button>
              <Button type="button" variant="default" disabled={!listo || Boolean(busy)}
                onClick={() => lanzar(true)}
                title="valida el manifiesto y enseña el plan sin escribir (el --dry-run del CLI)">
                {busy === 'comprobar' ? 'Comprobando…' : 'Comprobar'}
              </Button>
              <Button type="button" variant="primary" disabled={!listo || Boolean(busy)}
                onClick={() => lanzar(false)}>
                <Upload className="h-3.5 w-3.5" /> {busy === 'importar' ? 'Importando…' : 'Importar'}
              </Button>
            </div>
          </div>
        </DialogContent>
      )}
    </Dialog>
  )
}
