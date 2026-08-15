import { useState } from 'react'
import { api } from './api.js'
import { Input, PasswordInput } from './components/ui/input.jsx'
import { Button } from './components/ui/button.jsx'
import { AuthCard, Field } from './components/AuthCard.jsx'

// Lo que la consola es, en tres lineas. Van en la columna de marca (solo
// escritorio) para que la puerta de entrada diga a que estas entrando.
// Cortas a proposito: en mono con tracking .16em caben ~36 caracteres por
// linea en esa columna, y una linea partida en una palabra suelta se ve mal.
const FACTS = [
  'Manim Community · contenedor aislado',
  'Un render a la vez · telemetria viva',
  'Marca CO.DE Academy en cada video',
]

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
    <AuthCard
      onSubmit={submit}
      shake={Boolean(error)}
      title="ManimStudio"
      subtitle="La consola de renderizado de CO.DE Academy: escenas Manim, cola de trabajos y narración de los cursos, en un solo sitio."
      facts={FACTS}
      heading="Iniciar sesión"
    >
      <Field label="Usuario">
        <Input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          autoFocus
          required
        />
      </Field>

      <Field label="Contraseña">
        <PasswordInput
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </Field>

      {error && (
        <p role="alert" className="rounded-md border border-err/40 bg-err/10 px-3 py-2 text-[13px] text-err">
          {error}
        </p>
      )}

      <Button variant="primary" size="lg" disabled={busy} className="w-full">
        {busy ? 'Verificando…' : 'Entrar'}
      </Button>

      <p className="text-center text-[11.5px] text-muted">
        Acceso privado · coderesearch.space
      </p>
    </AuthCard>
  )
}
