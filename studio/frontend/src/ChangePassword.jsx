// Pantalla obligatoria de cambio de contraseña: se muestra en vez de la app
// cuando /api/me devuelve must_change_password=true (primer login del
// usuario recien creado). No es un dialogo cerrable — el backend bloquea el
// resto de la API con 403 hasta que la contraseña cambie.

import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { api } from './api.js'
import { OrbitGlyph } from './components/OrbitGlyph.jsx'
import { Input } from './components/ui/input.jsx'
import { Button } from './components/ui/button.jsx'
import { cn } from '@/lib/utils'
import { GlowCard } from './components/GlowCard.jsx'

export default function ChangePassword({ onChanged, onLogout }) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setError('Las contraseñas nuevas no coinciden')
      return
    }
    setBusy(true)
    setError('')
    try {
      await api.changePassword(currentPassword, newPassword)
      onChanged()
    } catch (err) {
      if (!err.status) setError('No se pudo conectar con el servidor')
      else if (err.status === 422) setError(err.message)
      else setError(`Error del servidor (${err.status})`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="relative grid h-full place-items-center overflow-hidden p-5">
      <div className="login__sky" aria-hidden="true" />
      <div aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_45%,var(--canvas)_100%)] opacity-80" />

      <GlowCard
        as="form"
        onSubmit={submit}
        customSize={true}
        glowColor="purple"
        className={cn(
          'relative z-[1] w-[min(420px,100%)] p-8',
          'shadow-[0_24px_70px_rgba(0,0,0,0.45)] backdrop-blur-xl',
          'animate-in fade-in slide-in-from-bottom-3 duration-500',
          error && 'animate-shake',
        )}
      >
        <div className="flex flex-col items-center gap-3 text-center">
          <OrbitGlyph state="idle" size={56} />
          <div>
            <h1 className="font-display text-[20px] font-semibold tracking-tight text-ink">
              Cambia tu contraseña
            </h1>
            <p className="mt-1 text-xs text-muted">
              Es tu primer inicio de sesión: elige una contraseña nueva antes de continuar.
            </p>
          </div>
        </div>

        <div className="mt-7 flex flex-col gap-4">
          <label className="flex flex-col gap-1.5">
            <span className="eyebrow">Contraseña actual</span>
            <Input
              type={showPass ? 'text' : 'password'}
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              autoComplete="current-password"
              autoFocus
              required
            />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="eyebrow">Contraseña nueva</span>
            <div className="relative">
              <Input
                type={showPass ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                aria-pressed={showPass}
                aria-label={showPass ? 'Ocultar contraseñas' : 'Mostrar contraseñas'}
                className="absolute right-1.5 top-1/2 grid -translate-y-1/2 place-items-center rounded p-1.5 text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
              >
                {showPass ? <EyeOff className="h-[18px] w-[18px]" /> : <Eye className="h-[18px] w-[18px]" />}
              </button>
            </div>
            <span className="text-[11px] text-faint">Al menos 8 caracteres.</span>
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="eyebrow">Repite la contraseña nueva</span>
            <Input
              type={showPass ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
              minLength={8}
              required
            />
          </label>

          {error && <p role="alert" className="text-center text-[13px] text-err">{error}</p>}

          <Button variant="primary" size="lg" disabled={busy} className="mt-1 w-full">
            {busy ? 'Guardando…' : 'Cambiar contraseña'}
          </Button>
          <button type="button" onClick={onLogout}
            className="text-center text-[12.5px] text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
            Cerrar sesión
          </button>
        </div>
      </GlowCard>
    </div>
  )
}
