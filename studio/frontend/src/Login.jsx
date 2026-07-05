import { useState } from 'react'
import { api } from './api.js'
import { OrbitGlyph } from './Header.jsx'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
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
      <form className="login__card" onSubmit={submit}>
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
        <label className="field">
          <span>Contraseña</span>
          <input type="password" value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password" required />
        </label>
        {error && <p className="login__error" role="alert">{error}</p>}
        <button className="btn btn--primary" disabled={busy}>
          {busy ? 'Verificando…' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}
