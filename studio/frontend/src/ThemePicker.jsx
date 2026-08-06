// Selector de tema: dropdown con muestra de paleta. Persiste en localStorage.
import { useEffect, useRef, useState } from 'react'
import { Check, Palette } from 'lucide-react'
import { THEMES, applyTheme, currentTheme } from './themes.js'
import { cn } from '@/lib/utils'

function Swatch({ colors }) {
  return (
    <span className="flex gap-1" aria-hidden="true">
      {colors.map((c) => (
        <span key={c} className="h-2.5 w-2.5 rounded-full ring-1 ring-white/15"
          style={{ background: c }} />
      ))}
    </span>
  )
}

export default function ThemePicker() {
  const [open, setOpen] = useState(false)
  const [theme, setTheme] = useState(currentTheme)
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return
    const close = (e) => { if (!ref.current?.contains(e.target)) setOpen(false) }
    const esc = (e) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', close)
    document.addEventListener('keydown', esc)
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('keydown', esc)
    }
  }, [open])

  const pick = (id) => { applyTheme(id); setTheme(id); setOpen(false) }
  const active = THEMES.find((t) => t.id === theme) || THEMES[0]

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        aria-haspopup="listbox"
        aria-expanded={open}
        title="Tema de la interfaz"
        className="flex h-9 items-center gap-2 rounded-md border border-line px-2.5 text-muted transition-colors hover:border-line-strong hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
      >
        <Palette className="h-4 w-4" />
        <Swatch colors={active.swatch} />
      </button>
      {open && (
        <div
          role="listbox"
          aria-label="temas"
          className="absolute right-0 top-[calc(100%+6px)] z-[70] min-w-[190px] overflow-hidden rounded-lg border border-line bg-surface p-1 shadow-2xl"
        >
          {THEMES.map((t) => (
            <button
              key={t.id}
              role="option"
              aria-selected={t.id === theme}
              onClick={() => pick(t.id)}
              className={cn(
                'flex w-full items-center gap-3 rounded-md px-2.5 py-2 text-sm text-ink transition-colors hover:bg-surface-2',
                t.id === theme && 'text-accent',
              )}
            >
              <Swatch colors={t.swatch} />
              <span className="flex-1 text-left">{t.name}</span>
              {t.id === theme && <Check className="h-4 w-4" />}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
