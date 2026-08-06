import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { api } from './api.js'
import { OrbitGlyph } from './components/OrbitGlyph.jsx'
import { Input } from './components/ui/input.jsx'
import { Button } from './components/ui/button.jsx'
import { cn } from '@/lib/utils'
import { GlowCard } from './components/GlowCard.jsx'


export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.login(username, password)
      onLogin()
    } catch (err) {
      if (!err.status) setError('No se pudo conectar con el servidor')
      else if (err.status === 429) setError(err.message)
      else if (err.status === 401) setError('Credenciales inválidas')
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
          'relative z-[1] w-[min(400px,100%)] p-8',
          'shadow-[0_24px_70px_rgba(0,0,0,0.45)] backdrop-blur-xl',
          'animate-in fade-in slide-in-from-bottom-3 duration-500',
          error && 'animate-shake',
        )}
      >
        <div className="flex flex-col items-center gap-3 text-center">
          <OrbitGlyph state="idle" size={56} />
          <div>
            <h1 className="font-display text-[22px] font-semibold tracking-tight text-ink">ManimStudio</h1>
            <p className="mt-1 text-xs text-muted">Consola privada de renderizado</p>
          </div>
          <span className="eyebrow mt-1">coderesearch.space</span>
        </div>

        <div className="mt-7 flex flex-col gap-4">
          <label className="flex flex-col gap-1.5">
            <span className="eyebrow">Usuario</span>
            <Input value={username} onChange={(e) => setUsername(e.target.value)}
              autoComplete="username" autoFocus required />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="eyebrow">Contraseña</span>
            <div className="relative">
              <Input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                aria-pressed={showPass}
                aria-label={showPass ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                className="absolute right-1.5 top-1/2 grid -translate-y-1/2 place-items-center rounded p-1.5 text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
              >
                {showPass ? <EyeOff className="h-[18px] w-[18px]" /> : <Eye className="h-[18px] w-[18px]" />}
              </button>
            </div>
          </label>

          {error && <p role="alert" className="text-center text-[13px] text-err">{error}</p>}

          <Button variant="primary" size="lg" disabled={busy} className="mt-1 w-full">
            {busy ? 'Verificando…' : 'Entrar'}
          </Button>
        </div>
      </GlowCard>
    </div>
  )
}
