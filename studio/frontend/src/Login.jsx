import { useState } from 'react'
import { api } from './api.js'
import { OrbitGlyph } from './Header.jsx'

function EyeIcon({ off }) {
  return off ? (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
      stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <path d="M3 3l18 18M10.6 10.7a2.8 2.8 0 0 0 3.9 4M6.6 6.8C4.6 8 3 9.8 2 12c1.8 3.9 5.5 6.5 10 6.5 1.9 0 3.7-.5 5.2-1.3M9.9 5.8A10.8 10.8 0 0 1 12 5.5c4.5 0 8.2 2.6 10 6.5a13 13 0 0 1-2.6 3.6" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
      stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <path d="M2 12c1.8-3.9 5.5-6.5 10-6.5S20.2 8.1 22 12c-1.8 3.9-5.5 6.5-10 6.5S3.8 15.9 2 12z" />
      <circle cx="12" cy="12" r="2.8" />
    </svg>
  )
}

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
    <div className="login">
      <div className="login__sky" aria-hidden="true" />
      <form className={`login__card${error ? ' login__card--shake' : ''}`}
        onSubmit={submit}>
        <div className="login__brand">
          <OrbitGlyph state="idle" />
          <h1 className="login__mark">MANIM·STUDIO</h1>
          <p className="login__sub">Consola privada de renderizado · coderesearch.space</p>
        </div>
        <label className="field">
          <span>Usuario</span>
          <input value={username} onChange={(e) => setUsername(e.target.value)}
            autoComplete="username" autoFocus required />
        </label>
        <label className="field field--pass">
          <span>Contraseña</span>
          <div className="field__wrap">
            <input type={showPass ? 'text' : 'password'} value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password" required />
            <button type="button" className="field__eye"
              onClick={() => setShowPass(!showPass)}
              aria-pressed={showPass}
              aria-label={showPass ? 'Ocultar contraseña' : 'Mostrar contraseña'}>
              <EyeIcon off={showPass} />
            </button>
          </div>
        </label>
        {error && <p className="login__error" role="alert">{error}</p>}
        <button className="btn btn--primary" disabled={busy}>
          {busy ? 'Verificando…' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}
