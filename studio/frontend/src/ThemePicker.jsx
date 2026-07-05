// Selector de tema: dropdown con muestra de paleta. Persiste en localStorage.

import { useEffect, useRef, useState } from 'react'
import { THEMES, applyTheme, currentTheme } from './themes.js'

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

  const pick = (id) => {
    applyTheme(id)
    setTheme(id)
    setOpen(false)
  }

  const active = THEMES.find((t) => t.id === theme)
  return (
    <div className="themepicker" ref={ref}>
      <button className="themepicker__btn" onClick={() => setOpen(!open)}
        aria-haspopup="listbox" aria-expanded={open} title="Tema de la interfaz">
        <span className="themepicker__dots" aria-hidden="true">
          {active.swatch.map((c) => (
            <span key={c} className="themepicker__dot" style={{ background: c }} />
          ))}
        </span>
        {active.name}
      </button>
      {open && (
        <div className="themepicker__menu" role="listbox" aria-label="temas">
          {THEMES.map((t) => (
            <button key={t.id} role="option" aria-selected={t.id === theme}
              className={`themepicker__item${t.id === theme ? ' themepicker__item--on' : ''}`}
              onClick={() => pick(t.id)}>
              <span className="themepicker__dots" aria-hidden="true">
                {t.swatch.map((c) => (
                  <span key={c} className="themepicker__dot" style={{ background: c }} />
                ))}
              </span>
              {t.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
